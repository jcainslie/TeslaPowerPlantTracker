import sqlite3
from flask import Blueprint, render_template, current_app
from datetime import datetime
from app.utils.auth import login_required



dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard():
    db_path = current_app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('''
        SELECT bill_date, usage_kwh, generation_kwh, usage_cost,
               generation_credit, efficiency, potential_kwh
        FROM bills
        WHERE bill_date IS NOT NULL
        ORDER BY bill_date ASC
    ''')
    rows = cur.fetchall()
    conn.close()

    chart_data = []
    total_usage = 0
    total_gen = 0
    total_potential = 0

    for row in rows:
        usage = row['usage_kwh'] or 0
        gen = row['generation_kwh'] or 0
        potential = row['potential_kwh'] or 0

        month_label = datetime.strptime(row['bill_date'], "%Y-%m-%d").strftime("%b %Y")
        net = (row['usage_cost'] or 0) - (row['generation_credit'] or 0)

        chart_data.append({
            "month": month_label,
            "usage": usage,
            "generation": gen,
            "efficiency": row['efficiency'] or 0,
            "net_cost": round(net, 2),
            "potential": potential,
        })

        total_usage += usage
        total_gen += gen
        total_potential += potential

    overall_eff = round((total_gen / total_usage) * 100, 2) if total_usage else 0
    system_health = round((total_gen / total_potential) * 100, 2) if total_potential else 0

    return render_template('dashboard.html',
        chart_data=chart_data,
        total_usage=round(total_usage, 2),
        total_generation=round(total_gen, 2),
        overall_efficiency=overall_eff,
        system_health=system_health
    )
