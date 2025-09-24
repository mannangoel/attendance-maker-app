from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import os
import json
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Database Models
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    semesters = db.relationship('Semester', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subjects = db.relationship('Subject', backref='semester', lazy=True, cascade='all, delete-orphan')

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    credits = db.Column(db.Integer, default=3)
    total_lectures = db.Column(db.Integer, default=60)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    timetable_slots = db.relationship('TimetableSlot', backref='subject', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='subject', lazy=True, cascade='all, delete-orphan')

class TimetableSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room = db.Column(db.String(50))

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    attended = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper Functions
def calculate_attendance_percentage(subject_id):
    """Calculate attendance percentage for a subject"""
    records = AttendanceRecord.query.filter_by(subject_id=subject_id).all()
    if not records:
        return 0.0
    
    total_lectures = len(records)
    attended_lectures = sum(1 for record in records if record.attended)
    return (attended_lectures / total_lectures) * 100 if total_lectures > 0 else 0.0

def calculate_aggregate_attendance():
    """Calculate overall attendance percentage across all subjects"""
    subjects = Subject.query.join(Semester).filter(Semester.is_active == True).all()
    if not subjects:
        return 0.0
    
    total_lectures = 0
    total_attended = 0
    
    for subject in subjects:
        records = AttendanceRecord.query.filter_by(subject_id=subject.id).all()
        total_lectures += len(records)
        total_attended += sum(1 for record in records if record.attended)
    
    return (total_attended / total_lectures) * 100 if total_lectures > 0 else 0.0

def calculate_lectures_needed(subject_id, target_percentage=75):
    """Calculate how many lectures needed to reach target attendance"""
    records = AttendanceRecord.query.filter_by(subject_id=subject_id).all()
    
    total_lectures = len(records)
    attended_lectures = sum(1 for record in records if record.attended)
    
    if total_lectures == 0:
        return {"lectures_to_attend": 0, "lectures_can_miss": 0, "current_percentage": 0}
    
    current_percentage = (attended_lectures / total_lectures) * 100
    
    # Calculate lectures needed to reach target
    lectures_to_attend = 0
    if current_percentage < target_percentage:
        # Need to attend more lectures
        # Formula: (attended + x) / (total + x) = target/100
        # Solving for x: x = (target * total - 100 * attended) / (100 - target)
        if target_percentage < 100:
            lectures_to_attend = max(0, int((target_percentage * total_lectures - 100 * attended_lectures) / (100 - target_percentage)))
    
    # Calculate lectures that can be missed while maintaining target
    lectures_can_miss = 0
    if current_percentage >= target_percentage:
        # Formula: attended / (total + x) >= target/100
        # Solving for x: x <= (100 * attended - target * total) / target
        if target_percentage > 0:
            lectures_can_miss = max(0, int((100 * attended_lectures - target_percentage * total_lectures) / target_percentage))
    
    return {
        "lectures_to_attend": lectures_to_attend,
        "lectures_can_miss": lectures_can_miss,
        "current_percentage": round(current_percentage, 2)
    }

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Logged in successfully!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful! Welcome to Attendance Tracker!', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

# Routes
@app.route('/')
@login_required
def index():
    """Dashboard showing overview of attendance"""
    active_semester = Semester.query.filter_by(is_active=True, user_id=current_user.id).first()
    if not active_semester:
        return redirect(url_for('manage_semesters'))
    
    subjects = Subject.query.filter_by(semester_id=active_semester.id).all()
    
    # Calculate attendance data for each subject
    subject_data = []
    for subject in subjects:
        attendance_percentage = calculate_attendance_percentage(subject.id)
        guidance = calculate_lectures_needed(subject.id)
        
        subject_data.append({
            'subject': subject,
            'attendance_percentage': round(attendance_percentage, 2),
            'guidance': guidance
        })
    
    aggregate_attendance = calculate_aggregate_attendance()
    
    return render_template('index.html', 
                         subjects=subject_data, 
                         aggregate_attendance=round(aggregate_attendance, 2),
                         semester=active_semester)

@app.route('/semesters')
@login_required
def manage_semesters():
    """Manage semesters"""
    semesters = Semester.query.filter_by(user_id=current_user.id).all()
    return render_template('semesters.html', semesters=semesters)

@app.route('/add_semester', methods=['GET', 'POST'])
@login_required
def add_semester():
    """Add a new semester"""
    if request.method == 'POST':
        # Deactivate all other semesters if this is set as active
        if request.form.get('is_active'):
            Semester.query.filter_by(user_id=current_user.id).update({'is_active': False})
        
        semester = Semester(
            name=request.form['name'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
            is_active=bool(request.form.get('is_active')),
            user_id=current_user.id
        )
        
        db.session.add(semester)
        db.session.commit()
        flash('Semester added successfully!', 'success')
        return redirect(url_for('manage_semesters'))
    
    return render_template('add_semester.html')

@app.route('/activate_semester/<int:semester_id>')
@login_required
def activate_semester(semester_id):
    """Activate a semester and deactivate others"""
    Semester.query.filter_by(user_id=current_user.id).update({'is_active': False})
    semester = Semester.query.filter_by(id=semester_id, user_id=current_user.id).first_or_404()
    semester.is_active = True
    db.session.commit()
    flash(f'Semester "{semester.name}" activated!', 'success')
    return redirect(url_for('manage_semesters'))

@app.route('/subjects')
@login_required
def manage_subjects():
    """Manage subjects for active semester"""
    active_semester = Semester.query.filter_by(is_active=True, user_id=current_user.id).first()
    if not active_semester:
        flash('Please create and activate a semester first.', 'warning')
        return redirect(url_for('manage_semesters'))
    
    subjects = Subject.query.filter_by(semester_id=active_semester.id).all()
    return render_template('subjects.html', subjects=subjects, semester=active_semester)

@app.route('/add_subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    """Add a new subject"""
    active_semester = Semester.query.filter_by(is_active=True, user_id=current_user.id).first()
    if not active_semester:
        flash('Please create and activate a semester first.', 'warning')
        return redirect(url_for('manage_semesters'))
    
    if request.method == 'POST':
        subject = Subject(
            name=request.form['name'],
            code=request.form['code'],
            credits=int(request.form['credits']),
            total_lectures=int(request.form['total_lectures']),
            semester_id=active_semester.id
        )
        
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('manage_subjects'))
    
    return render_template('add_subject.html', semester=active_semester)

@app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    """Edit an existing subject"""
    subject = Subject.query.join(Semester).filter(
        Subject.id == subject_id,
        Semester.user_id == current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        subject.name = request.form['name']
        subject.code = request.form['code']
        subject.credits = int(request.form['credits'])
        subject.total_lectures = int(request.form['total_lectures'])
        
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('manage_subjects'))
    
    return render_template('edit_subject.html', subject=subject)

@app.route('/delete_subject/<int:subject_id>')
@login_required
def delete_subject(subject_id):
    """Delete a subject"""
    subject = Subject.query.join(Semester).filter(
        Subject.id == subject_id,
        Semester.user_id == current_user.id
    ).first_or_404()
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('manage_subjects'))

@app.route('/timetable')
@login_required
def view_timetable():
    """View and manage timetable"""
    active_semester = Semester.query.filter_by(is_active=True, user_id=current_user.id).first()
    if not active_semester:
        flash('Please create and activate a semester first.', 'warning')
        return redirect(url_for('manage_semesters'))
    
    subjects = Subject.query.filter_by(semester_id=active_semester.id).all()
    
    # Organize timetable by day and time
    timetable_data = defaultdict(list)
    for subject in subjects:
        for slot in subject.timetable_slots:
            timetable_data[slot.day_of_week].append({
                'subject': subject,
                'slot': slot
            })
    
    # Sort by start time for each day
    for day in timetable_data:
        timetable_data[day].sort(key=lambda x: x['slot'].start_time)
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    return render_template('timetable.html', 
                         timetable_data=dict(timetable_data), 
                         subjects=subjects, 
                         days=days,
                         semester=active_semester)

@app.route('/add_timetable_slot', methods=['POST'])
@login_required
def add_timetable_slot():
    """Add a timetable slot for a subject"""
    # Verify the subject belongs to the current user
    subject = Subject.query.join(Semester).filter(
        Subject.id == int(request.form['subject_id']),
        Semester.user_id == current_user.id
    ).first_or_404()
    slot = TimetableSlot(
        subject_id=subject.id,
        day_of_week=int(request.form['day_of_week']),
        start_time=datetime.strptime(request.form['start_time'], '%H:%M').time(),
        end_time=datetime.strptime(request.form['end_time'], '%H:%M').time(),
        room=request.form['room']
    )
    
    db.session.add(slot)
    db.session.commit()
    flash('Timetable slot added successfully!', 'success')
    return redirect(url_for('view_timetable'))

@app.route('/delete_timetable_slot/<int:slot_id>')
@login_required
def delete_timetable_slot(slot_id):
    """Delete a timetable slot"""
    slot = TimetableSlot.query.join(Subject).join(Semester).filter(
        TimetableSlot.id == slot_id,
        Semester.user_id == current_user.id
    ).first_or_404()
    db.session.delete(slot)
    db.session.commit()
    flash('Timetable slot deleted successfully!', 'success')
    return redirect(url_for('view_timetable'))

@app.route('/attendance')
@login_required
def mark_attendance():
    """Mark daily attendance"""
    active_semester = Semester.query.filter_by(is_active=True, user_id=current_user.id).first()
    if not active_semester:
        flash('Please create and activate a semester first.', 'warning')
        return redirect(url_for('manage_semesters'))
    
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    
    subjects = Subject.query.filter_by(semester_id=active_semester.id).all()
    
    # Get existing attendance records for the selected date
    attendance_data = {}
    for subject in subjects:
        record = AttendanceRecord.query.filter_by(
            subject_id=subject.id,
            date=selected_date_obj
        ).first()
        attendance_data[subject.id] = record
    
    return render_template('attendance.html', 
                         subjects=subjects, 
                         selected_date=selected_date,
                         attendance_data=attendance_data,
                         semester=active_semester)

@app.route('/save_attendance', methods=['POST'])
@login_required
def save_attendance():
    """Save attendance records for a specific date"""
    selected_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    
    for subject_id in request.form.getlist('subject_ids'):
        subject_id = int(subject_id)
        
        # Verify the subject belongs to the current user
        subject = Subject.query.join(Semester).filter(
            Subject.id == subject_id,
            Semester.user_id == current_user.id
        ).first()
        
        if not subject:
            continue  # Skip if subject doesn't belong to user
        attended = f'attended_{subject_id}' in request.form
        notes = request.form.get(f'notes_{subject_id}', '')
        
        # Check if record already exists
        existing_record = AttendanceRecord.query.filter_by(
            subject_id=subject_id,
            date=selected_date
        ).first()
        
        if existing_record:
            existing_record.attended = attended
            existing_record.notes = notes
        else:
            new_record = AttendanceRecord(
                subject_id=subject_id,
                date=selected_date,
                attended=attended,
                notes=notes
            )
            db.session.add(new_record)
    
    db.session.commit()
    flash('Attendance saved successfully!', 'success')
    return redirect(url_for('mark_attendance', date=selected_date.strftime('%Y-%m-%d')))

@app.route('/attendance_report')
@login_required
def attendance_report():
    """View detailed attendance report"""
    active_semester = Semester.query.filter_by(is_active=True, user_id=current_user.id).first()
    if not active_semester:
        flash('Please create and activate a semester first.', 'warning')
        return redirect(url_for('manage_semesters'))
    
    subjects = Subject.query.filter_by(semester_id=active_semester.id).all()
    
    report_data = []
    for subject in subjects:
        records = AttendanceRecord.query.filter_by(subject_id=subject.id).order_by(AttendanceRecord.date.desc()).all()
        attendance_percentage = calculate_attendance_percentage(subject.id)
        guidance = calculate_lectures_needed(subject.id)
        
        report_data.append({
            'subject': subject,
            'records': records,
            'attendance_percentage': round(attendance_percentage, 2),
            'guidance': guidance,
            'total_lectures': len(records),
            'attended_lectures': sum(1 for r in records if r.attended)
        })
    
    aggregate_attendance = calculate_aggregate_attendance()
    
    return render_template('attendance_report.html', 
                         report_data=report_data,
                         aggregate_attendance=round(aggregate_attendance, 2),
                         semester=active_semester)

@app.route('/api/attendance_data')
@login_required
def api_attendance_data():
    """API endpoint for attendance data (for charts/graphs)"""
    active_semester = Semester.query.filter_by(is_active=True, user_id=current_user.id).first()
    if not active_semester:
        return jsonify({'error': 'No active semester'})
    
    subjects = Subject.query.filter_by(semester_id=active_semester.id).all()
    
    data = []
    for subject in subjects:
        attendance_percentage = calculate_attendance_percentage(subject.id)
        data.append({
            'subject_name': subject.name,
            'subject_code': subject.code,
            'attendance_percentage': round(attendance_percentage, 2)
        })
    
    return jsonify({
        'subjects': data,
        'aggregate_attendance': round(calculate_aggregate_attendance(), 2)
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Get port from environment variable or default to 5001
    port = int(os.environ.get('PORT', 5001))
    # Use 0.0.0.0 for deployment, localhost for local development
    host = '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
    app.run(debug=True, host=host, port=port)