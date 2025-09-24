# Student Attendance Tracker 📚

[![CI/CD Pipeline](https://github.com/mannangoel/attendance-maker-app/actions/workflows/ci.yml/badge.svg)](https://github.com/mannangoel/attendance-maker-app/actions/workflows/ci.yml)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive web application for students to track their attendance, manage subjects, and maintain the required 75% attendance across all subjects. Built with Flask, SQLAlchemy, and Bootstrap for a modern, responsive experience.

## 🚀 Live Demo

🌐 **[View Live Application](https://attendance-maker-app.herokuapp.com)** *(Deploy to get live link)*

> **Note**: To get a live demo link, you can deploy this application to:
> - [Heroku](https://heroku.com) (Free tier available)
> - [Railway](https://railway.app) (Free deployments)
> - [Render](https://render.com) (Free static sites)
> - [PythonAnywhere](https://pythonanywhere.com) (Free Python hosting)
>
> After deployment, update this README with your actual live URL.

## 📸 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)
*Real-time attendance overview with smart guidance*

### Attendance Marking
![Attendance](screenshots/attendance.png)
*Easy daily attendance marking interface*

### Analytics & Reports
![Reports](screenshots/reports.png)
*Detailed subject-wise analysis and trends*

## Features

### 📚 Subject Management
- Add, edit, and delete subjects for each semester
- Track credits and total lectures per subject
- Organize subjects by semester

### 📅 Timetable Management
- Create and manage weekly timetable
- Add time slots for each subject
- Visual timetable view with room information

### ✅ Attendance Tracking
- Mark daily attendance for each subject
- Add notes for specific attendance records
- Track historical attendance data

### 📊 Analytics & Insights
- Real-time attendance percentage calculation
- Subject-wise and aggregate attendance tracking
- Visual charts and progress bars
- Attendance reports with detailed breakdowns

### 🎯 Smart Guidance System
- Automatic calculation of lectures needed to reach 75%
- Alerts for subjects below target attendance
- Shows how many lectures can be missed while maintaining 75%
- Color-coded status indicators (Good/Warning/Critical)

### 📱 Responsive Design
- Bootstrap-based responsive UI
- Mobile-friendly interface
- Dark/light mode compatible

## Installation & Setup

### Prerequisites
- Python 3.7+ installed on your system
- Git (for cloning the repository)
- A modern web browser

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/mannangoel/attendance-maker-app.git
   cd attendance-maker-app
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and go to: `http://localhost:5001`

## 🌐 Deployment

### Deploy to Heroku (Recommended)

1. **Create a Heroku account** at [heroku.com](https://heroku.com)

2. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

3. **Create a Heroku app**:
   ```bash
   heroku create attendance-maker-app-[your-username]
   ```

4. **Add a Procfile** (create this file in your project root):
   ```
   web: python app.py
   ```

5. **Deploy**:
   ```bash
   git add .
   git commit -m "Add Heroku deployment config"
   git push heroku main
   ```

6. **Open your app**:
   ```bash
   heroku open
   ```

### Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-deploy your Flask app
4. Get your live URL from the Railway dashboard

### Deploy to Render

1. Go to [render.com](https://render.com)
2. Connect your GitHub repository
3. Select "Web Service"
4. Use build command: `pip install -r requirements.txt`
5. Use start command: `python app.py`

## Getting Started

### Step 1: Create a Semester
1. Go to "Manage" → "Semesters"
2. Click "Add Semester"
3. Enter semester name and dates
4. Set as active semester

### Step 2: Add Subjects
1. Go to "Manage" → "Subjects"
2. Click "Add Subject"
3. Enter subject details (name, code, credits, total lectures)

### Step 3: Set up Timetable (Optional)
1. Go to "Timetable"
2. Click "Add Slot"
3. Select subject, day, time, and room

### Step 4: Mark Attendance
1. Go to "Mark Attendance"
2. Select date (defaults to today)
3. Mark present/absent for each subject
4. Add notes if needed

### Step 5: View Reports
1. Dashboard shows overall statistics
2. "Reports" shows detailed subject-wise analysis
3. Charts visualize attendance trends

## Key Calculations

### Attendance Percentage
```
Attendance % = (Attended Lectures / Total Lectures) × 100
```

### Lectures Needed to Reach 75%
```
Lectures Needed = (75 × Total - 100 × Attended) / (100 - 75)
```

### Lectures Can Miss While Maintaining 75%
```
Can Miss = (100 × Attended - 75 × Total) / 75
```

## Database Schema

### Tables
- **Semester**: Stores semester information
- **Subject**: Stores subject details linked to semesters
- **TimetableSlot**: Stores weekly schedule information
- **AttendanceRecord**: Stores daily attendance records

### Relationships
- One semester can have multiple subjects
- One subject can have multiple timetable slots
- One subject can have multiple attendance records

## File Structure

```
attendance-maker-app/
├── .github/
│   └── workflows/
│       └── ci.yml            # CI/CD pipeline configuration
├── templates/                # HTML templates
│   ├── base.html            # Base template with navigation
│   ├── index.html           # Dashboard
│   ├── attendance.html      # Mark attendance
│   ├── timetable.html       # Timetable management
│   ├── subjects.html        # Subject management
│   ├── semesters.html       # Semester management
│   ├── attendance_report.html # Detailed reports
│   ├── add_subject.html
│   ├── edit_subject.html
│   └── add_semester.html
├── static/
│   └── style.css            # Custom CSS styles
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
└── attendance.db           # SQLite database (auto-created)
```

## Technologies Used

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Charts**: Chart.js
- **Database**: SQLite
- **Icons**: Bootstrap Icons

## Features Highlights

### 🎯 Smart Attendance Guidance
The application automatically calculates:
- How many lectures you need to attend to reach 75%
- How many lectures you can afford to miss
- Real-time status updates as you mark attendance

### 📊 Visual Analytics
- Color-coded progress bars
- Interactive charts
- Quick stats on dashboard
- Detailed subject-wise breakdowns

### 💡 User-Friendly Interface
- Intuitive navigation
- Quick action buttons
- Responsive design for all devices
- Flash messages for user feedback

### 🔄 Flexible Management
- Edit subjects and attendance records
- Multiple semester support
- Timetable integration
- Historical data preservation

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Ensure all tests pass before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/) - The Python web framework
- Styled with [Bootstrap 5](https://getbootstrap.com/) - For responsive design
- Charts powered by [Chart.js](https://www.chartjs.org/) - For beautiful visualizations
- Icons from [Bootstrap Icons](https://icons.getbootstrap.com/) - For consistent iconography

## 📞 Support

If you have any questions or run into issues:

1. Check the [Issues](https://github.com/mannangoel/attendance-maker-app/issues) page
2. Create a new issue if your problem isn't already listed
3. Provide detailed information about your setup and the issue

## 🚀 Roadmap

- [ ] Add export functionality (PDF reports)
- [ ] Email notifications for low attendance
- [ ] Mobile app version
- [ ] Multi-user support with authentication
- [ ] Integration with university systems
- [ ] Attendance prediction algorithms

---

**Made with ❤️ by [mannangoel](https://github.com/mannangoel)**

If this project helped you, please consider giving it a ⭐️!