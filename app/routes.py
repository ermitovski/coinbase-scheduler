from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from app import config
from app.trading import get_account_balance, get_transaction_history
from app.scheduler import get_next_run_time, manual_buy

# Create a Blueprint for the main routes
main_bp = Blueprint('main', __name__)

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
def index():
    """Home page - shows current status and next scheduled buy"""
    return render_template('index.html', 
                          logged_in=session.get('logged_in', False),
                          next_buy_time=get_next_run_time(),
                          product_id=config.PRODUCT_ID,
                          daily_amount=config.DAILY_AMOUNT)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    """Logout route"""
    session.pop('logged_in', None)
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page - protected area to view and manage trades"""
    balance = get_account_balance()
    transactions = get_transaction_history()
    next_buy_time = get_next_run_time()
    
    return render_template('dashboard.html',
                          balance=balance,
                          transactions=transactions,
                          next_buy_time=next_buy_time,
                          product_id=config.PRODUCT_ID,
                          daily_amount=config.DAILY_AMOUNT)

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Settings page - configure trading parameters"""
    if request.method == 'POST':
        # This would typically update the settings in a database or config file
        # For now, we'll just acknowledge the request
        flash('Settings updated successfully', 'success')
        return redirect(url_for('main.settings'))
    
    return render_template('settings.html',
                          product_id=config.PRODUCT_ID,
                          daily_amount=config.DAILY_AMOUNT,
                          buy_time=config.BUY_TIME)

@main_bp.route('/api/manual-buy', methods=['POST'])
@login_required
def api_manual_buy():
    """API endpoint to manually trigger a buy operation"""
    try:
        result = manual_buy()
        return jsonify({'success': True, 'transaction': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/balance')
@login_required
def api_balance():
    """API endpoint to get current balance"""
    try:
        balance = get_account_balance()
        return jsonify({'success': True, 'balance': balance})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/transactions')
@login_required
def api_transactions():
    """API endpoint to get transaction history"""
    try:
        transactions = get_transaction_history()
        return jsonify({'success': True, 'transactions': transactions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
