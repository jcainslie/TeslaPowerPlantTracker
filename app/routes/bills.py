import os
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
from calendar import monthrange
from dotenv import load_dotenv
from app.utils.auth import login_required
from app.utils.solar import get_monthly_ghi

# Load .env variables
load_dotenv()
SYSTEM_KW = float(os.getenv("SYSTEM_KW", 6.2))
PERFORMANCE_RATIO = float(os.getenv("PERFORMANCE_RATIO", 0.80))

bills_bp = Blueprint('bills', __name__, url_prefix='/bills')


@bills_bp.route('/')
@login_required
def bill_list():
    db_path = current_app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('SELECT id, filename, bill_date FROM bills ORDER BY bill_date DESC')
    bills = cur.fetchall()
    conn.close()

    return render_template('bills.html', bills=bills)


@bills_bp.route('/upload-ajax', methods=['POST'])
@login_required
def upload_bill_ajax():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return {'status': 'error', 'message': 'Invalid file'}, 400

    # Get form fields
    bill_date = request.form.get('bill_date')
    base_kwh = float(request.form.get('base_kwh') or 0)
    peak_kwh = float(request.form.get('peak_kwh') or 0)
    usage_kwh = base_kwh + peak_kwh
    usage_cost = float(request.form.get('usage_cost') or 0)
    generation_kwh = float(request.form.get('generation_kwh') or 0)
    generation_credit = float(request.form.get('generation_credit') or 0)
    efficiency = (generation_kwh / usage_kwh * 100) if usage_kwh > 0 else 0

    # Compute GHI and Potential
    try:
        dt = datetime.strptime(bill_date, "%Y-%m-%d")
        month_abbr = dt.strftime("%b").upper()
        days = monthrange(dt.year, dt.month)[1]
        lat = float(current_app.config['LATITUDE'])
        lon = float(current_app.config['LONGITUDE'])

        ghi = get_monthly_ghi(lat, lon, month_abbr)
        potential = ghi * days * SYSTEM_KW * PERFORMANCE_RATIO if ghi else None
    except Exception as e:
        print(f"[GHI ERROR] {e}")
        ghi = None
        potential = None

    # Save PDF file
    db_path = current_app.config['DATABASE']
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    filename = secure_filename(file.filename)
    save_path = os.path.join(upload_dir, filename)
    file.save(save_path)

    # Insert into DB
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Prevent duplicates
    cur.execute('SELECT 1 FROM bills WHERE filename = ?', (filename,))
    if cur.fetchone():
        print(f"[SKIP] File already uploaded: {filename}")
        conn.close()
        return {'status': 'duplicate'}, 200

    cur.execute('''
        INSERT INTO bills (
            filename, bill_date,
            usage_kwh, usage_cost,
            generation_kwh, generation_credit,
            efficiency, ghi_kwh_m2, potential_kwh
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        filename, bill_date,
        usage_kwh, usage_cost,
        generation_kwh, generation_credit,
        efficiency, ghi, potential
    ))

    conn.commit()
    conn.close()
    return {'status': 'success'}, 200


@bills_bp.route('/file/<path:filename>')
@login_required
def serve_file(filename):
    upload_dir = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    full_path = os.path.join(upload_dir, filename)

    if not os.path.exists(full_path):
        print(f"[404] File not found: {full_path}")
    else:
        print(f"[200] Serving file: {full_path}")

    return send_from_directory(upload_dir, filename)


@bills_bp.route('/delete/<int:bill_id>', methods=['POST'])
@login_required
def delete_bill(bill_id):
    db_path = current_app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get filename to delete the actual PDF file too
    cur.execute('SELECT filename FROM bills WHERE id = ?', (bill_id,))
    row = cur.fetchone()
    if row:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], row[0])
        if os.path.exists(file_path):
            os.remove(file_path)

    cur.execute('DELETE FROM bills WHERE id = ?', (bill_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('bills.bill_list'))
