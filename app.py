import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from models import db, User, CarbonEntry
from services import calculate_co2, get_suggestions

load_dotenv()

app = Flask(__name__, template_folder='Templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key-for-dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///footprint.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'register':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            account_type = request.form.get('account_type', 'personal')
            company_name = request.form.get('company_name') if account_type == 'company' else None
            
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email address already exists.')
                return redirect(url_for('auth'))
                
            new_user = User(username=username, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'), account_type=account_type, company_name=company_name)
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)
            return redirect(url_for('dashboard'))
            
        elif action == 'login':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            # In Werkzeug 3, pbkdf2:sha256 is the default
            if not user or not check_password_hash(user.password, password):
                flash('Please check your login details and try again.')
                return redirect(url_for('auth'))
                
            login_user(user)
            return redirect(url_for('dashboard'))
            
    return render_template('auth.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.account_type == 'company':
        return render_template('company_dashboard.html', name=current_user.username, company=current_user.company_name)
    return render_template('dashboard.html', name=current_user.username)

@app.route('/api/calculate', methods=['POST'])
@login_required
def api_calculate():
    data = request.json
    activity_type = data.get('activity_type')
    value = float(data.get('value', 0))
    unit = data.get('unit')
    
    # Calculate CO2 using our service
    co2_amount = calculate_co2(activity_type, value, unit)
    
    # Save to db
    entry = CarbonEntry(
        user_id=current_user.id,
        activity_type=activity_type,
        value=value,
        unit=unit,
        carbon_emission=co2_amount
    )
    db.session.add(entry)
    db.session.commit()
    
    advice = get_suggestions(activity_type, co2_amount)
    message_html = f"Added <b>{co2_amount:.2f} kg CO2e</b>.<br>🌳 You'd need to plant ~<b>{advice['trees']} tree(s)</b> to offset this yearly.<br>💡 <i>Tip: {advice['tip']}</i>"
    
    return jsonify({
        'success': True,
        'carbon_emission': co2_amount,
        'message_html': message_html
    })

@app.route('/api/history', methods=['GET'])
@login_required
def api_history():
    entries = CarbonEntry.query.filter_by(user_id=current_user.id).order_by(CarbonEntry.date.asc()).all()
    result = [{
        'date': entry.date.strftime('%Y-%m-%d %H:%M:%S'),
        'activity_type': entry.activity_type,
        'value': entry.value,
        'unit': entry.unit,
        'carbon_emission': entry.carbon_emission
    } for entry in entries]
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
