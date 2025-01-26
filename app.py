# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teacherconnect.db'
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # Replace with a secure random key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)  # 'student' or 'teacher'

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    subjects = db.Column(db.String(255), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, default=0.0)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    # Database Models
    '''
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)  # 'student' or 'teacher'
    '''
    # Relationships
    teacher_profile = db.relationship('TeacherProfile', backref='user', uselist=False)
    student_classes = db.relationship('ClassBooking', backref='student', lazy='dynamic')

class TeacherProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subjects = db.Column(db.String(255), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    availability = db.Column(db.JSON)  # Store availability as JSON

class ClassBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
'''
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
'''

# Render Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        


        return redirect(url_for('login'))  # Redirect to login page after successful registration
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(email=data['email']).first()
        
        if user and bcrypt.check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=user.id)
            return redirect(url_for('student_dashboard') if user.user_type == 'student' else url_for('teacher_dashboard'))
        
        return 'Invalid credentials', 401
    
    return render_template('login2.html')
# Dashboard Routes


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'student':
        return student_dashboard()
    else:
        return teacher_dashboard()

def student_dashboard():
    # Upcoming classes for student
    upcoming_classes = ClassBooking.query.filter_by(
        student_id=current_user.id, 
        status='scheduled'
    ).all()
    
    return render_template('student_dashboard.html', 
        user=current_user, 
        classes=upcoming_classes
    )

def teacher_dashboard():
    # Classes for teacher
    teacher_classes = ClassBooking.query.filter_by(
        teacher_id=current_user.id
    ).all()
    


# Teacher Dashboard
@app.route('/teacher/dashboard', methods=['GET'])
@jwt_required()
def teacher_dashboard():
    current_user_id = get_jwt_identity()
    teacher = Teacher.query.filter_by(user_id=current_user_id).first()
    classes = Class.query.filter_by(teacher_id=teacher.id).all()
    
    return render_template('teacher_dashboard.html', classes=classes)

# Student Dashboard
@app.route('/student/dashboard', methods=['GET'])
@jwt_required()
def student_dashboard():
    current_user_id = get_jwt_identity()
    upcoming_classes = Class.query.filter_by(student_id=current_user_id, status='scheduled').all()
    
    return render_template('student_dashboard.html', upcoming_classes=upcoming_classes)

# Book Class Route
@app.route('/book_class', methods=['GET', 'POST'])
@jwt_required()
def book_class():
    if request.method == 'POST':
        data = request.form
        current_user_id = get_jwt_identity()
        
        new_class = Class(
            teacher_id=data['teacher_id'],
            student_id=current_user_id,
            subject=data['subject'],
            date=datetime.fromisoformat(data['date'])
        )
        
        db.session.add(new_class)
        db.session.commit()
        
        return redirect(url_for('student_dashboard'))  # Redirect to student dashboard after booking
        
    return render_template('book_class.html')
