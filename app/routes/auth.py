from flask import Blueprint, render_template, request, redirect, session, url_for, current_app, flash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == current_app.config['APP_USERNAME'] and password == current_app.config['APP_PASSWORD']:
            session['logged_in'] = True
            return redirect(url_for('dashboard.dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
