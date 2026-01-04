from flask import Flask, render_template, redirect, url_for, flash, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import csv
from io import StringIO
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cpe_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    records = db.relationship('CPERecord', backref='user', lazy=True, cascade='all, delete-orphan')

class CPERecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    training_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False, default='General')
    hours = db.Column(db.Float, nullable=False)
    link = db.Column(db.String(500))
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def dashboard():
    total_hours = db.session.query(db.func.sum(CPERecord.hours)).filter_by(user_id=current_user.id).scalar() or 0
    recent_records = CPERecord.query.filter_by(user_id=current_user.id).order_by(CPERecord.date_added.desc()).limit(5).all()
    
    # Get hours by category
    category_hours = db.session.query(
        CPERecord.category,
        db.func.sum(CPERecord.hours)
    ).filter_by(user_id=current_user.id).group_by(CPERecord.category).all()
    
    return render_template('dashboard.html', 
                         total_hours=total_hours, 
                         recent_records=recent_records,
                         category_hours=category_hours)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_record():
    if request.method == 'POST':
        training_name = request.form.get('training_name')
        category = request.form.get('category')
        hours = request.form.get('hours')
        link = request.form.get('link')
        
        try:
            hours = float(hours)
        except ValueError:
            flash('Invalid hours value', 'danger')
            return redirect(url_for('add_record'))
        
        record = CPERecord(
            user_id=current_user.id,
            training_name=training_name,
            category=category,
            hours=hours,
            link=link
        )
        db.session.add(record)
        db.session.commit()
        
        flash('Training record added successfully!', 'success')
        return redirect(url_for('records'))
    
    # Get existing categories for dropdown
    existing_categories = db.session.query(CPERecord.category).filter_by(
        user_id=current_user.id
    ).distinct().all()
    categories = [cat[0] for cat in existing_categories]
    
    return render_template('add_record.html', categories=categories)

@app.route('/records')
@login_required
def records():
    user_records = CPERecord.query.filter_by(user_id=current_user.id).order_by(CPERecord.date_added.desc()).all()
    return render_template('records.html', records=user_records)

@app.route('/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    record = CPERecord.query.get_or_404(record_id)
    
    if record.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('records'))
    
    if request.method == 'POST':
        record.training_name = request.form.get('training_name')
        record.category = request.form.get('category')
        record.link = request.form.get('link')
        
        try:
            record.hours = float(request.form.get('hours'))
        except ValueError:
            flash('Invalid hours value', 'danger')
            return redirect(url_for('edit_record', record_id=record_id))
        
        record.date_modified = datetime.utcnow()
        db.session.commit()
        
        flash('Record updated successfully!', 'success')
        return redirect(url_for('records'))
    
    # Get existing categories for dropdown
    existing_categories = db.session.query(CPERecord.category).filter_by(
        user_id=current_user.id
    ).distinct().all()
    categories = [cat[0] for cat in existing_categories]
    
    return render_template('edit_record.html', record=record, categories=categories)

@app.route('/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    record = CPERecord.query.get_or_404(record_id)
    
    if record.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('records'))
    
    db.session.delete(record)
    db.session.commit()
    
    flash('Record deleted successfully!', 'success')
    return redirect(url_for('records'))

@app.route('/export', methods=['GET', 'POST'])
@login_required
def export():
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        query = CPERecord.query.filter_by(user_id=current_user.id)
        
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(CPERecord.date_added >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            query = query.filter(CPERecord.date_added <= end_datetime)
        
        records = query.order_by(CPERecord.date_added.desc()).all()
        
        # Generate CSV
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['Training Name', 'Category', 'Hours', 'Link', 'Date Added'])
        
        for record in records:
            writer.writerow([
                record.training_name,
                record.category,
                record.hours,
                record.link or '',
                record.date_added.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=cpe_records_{start_date or 'all'}_{end_date or 'all'}.csv"
        output.headers["Content-type"] = "text/csv"
        
        return output
    
    return render_template('export.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)