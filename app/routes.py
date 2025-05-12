from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
import logging
import traceback
from app import config
from app.trading import get_account_balance, get_transaction_history, get_client
from app.scheduler import get_next_run_time, manual_buy, update_scheduler

# Set up logging
logger = logging.getLogger('coinbase_app.routes')

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
    all_transactions = get_transaction_history()
    
    # Get only the most recent 5 transactions for the Recent Activity section
    recent_transactions = all_transactions[-5:] if all_transactions else []
    # Reverse to show newest first
    recent_transactions.reverse()
    
    next_buy_time = get_next_run_time()
    
    return render_template('dashboard.html',
                          balance=balance,
                          transactions=all_transactions,  # For Transaction History
                          recent_transactions=recent_transactions,  # For Recent Activity
                          next_buy_time=next_buy_time,
                          product_id=config.PRODUCT_ID,
                          daily_amount=config.DAILY_AMOUNT)

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Settings page - configure trading parameters"""
    error = None
    
    if request.method == 'POST':
        try:
            # Get form values
            product_id = request.form.get('product_id')
            daily_amount = request.form.get('daily_amount')
            buy_time = request.form.get('buy_time')
            
            # Update configuration
            updated = config.update_settings(
                new_product_id=product_id,
                new_daily_amount=daily_amount,
                new_buy_time=buy_time
            )
            
            if updated:
                # Update the scheduler with new settings
                update_scheduler()
                flash('Settings updated successfully', 'success')
                logger.info(f"Settings updated: Product ID={config.PRODUCT_ID}, Daily Amount={config.DAILY_AMOUNT}, Buy Time={config.BUY_TIME}")
            else:
                flash('No changes detected', 'info')
                
        except ValueError as e:
            error = str(e)
            flash(f'Error updating settings: {error}', 'danger')
            logger.error(f"Settings update failed: {error}")
        except Exception as e:
            error = str(e)
            flash(f'Unexpected error: {error}', 'danger')
            logger.error(f"Unexpected error updating settings: {error}")
    
    return render_template('settings.html',
                          product_id=config.PRODUCT_ID,
                          daily_amount=config.DAILY_AMOUNT,
                          buy_time=config.BUY_TIME,
                          error=error)

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

@main_bp.route('/api/debug-coinbase', methods=['GET'])
@login_required
def api_debug_coinbase():
    """API endpoint to debug Coinbase API responses"""
    try:
        client = get_client()
        
        # Get product info
        product_id = config.PRODUCT_ID
        product_info = client.get_product(product_id=product_id)
        
        # Extract basic info for easier debugging
        if hasattr(product_info, '__dict__'):
            # Try to convert to dict if possible
            product_dict = {
                'type': str(type(product_info)),
                'dir': str(dir(product_info))
            }
            
            # Add all attributes from the object
            for attr in dir(product_info):
                if not attr.startswith('_'):  # Skip private attributes
                    try:
                        value = getattr(product_info, attr)
                        if not callable(value):  # Skip methods
                            product_dict[attr] = str(value)
                    except Exception as e:
                        product_dict[f"error_{attr}"] = str(e)
        else:
            # If it's not an object with __dict__, just return string representation
            product_dict = {
                'type': str(type(product_info)),
                'string_repr': str(product_info)
            }
        
        return jsonify({
            'success': True,
            'product_info': product_dict
        })
    except Exception as e:
        logger.error(f"Debug API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': str(traceback.format_exc())
        }), 500
