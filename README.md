<div align="center">

# 📋 TaskFlow - Modern Task Management Web App

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-black.svg?logo=flask&logoColor=white)](https://palletsprojects.com/p/flask/)
[![SQLite](https://img.shields.io/badge/SQLite-SQLAlchemy-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3-7952B3.svg?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A clean, full-stack Task Management Dashboard built with **Python (Flask)**, **SQLite (SQLAlchemy)**, **Tailwind CSS**, and **Bootstrap 5**. Designed for seamless task scheduling, live statistics tracking, and responsive productivity workflows.

</div>

---

## 🌟 Highlights & Features

- **⚡ Full CRUD Task Management**: Create, list, edit, and delete tasks with instant feedback.
- **📊 Real-time Dashboard Analytics**:
  - Live metric summary cards (Total, Completed, In Progress, Pending & Overdue).
  - Animated completion rate progress bar.
  - Interactive **Chart.js** status distribution (doughnut) and priority breakdown (bar).
  - Upcoming deadlines widget with quick completion action.
- **🔍 Advanced Search, Filtering & Sorting**:
  - Full-text search across titles and descriptions.
  - Filter by status (`Pending`, `In Progress`, `Completed`, `Overdue`).
  - Filter by priority (`Low`, `Medium`, `High`, `Urgent`).
  - Sort by due date (soonest / latest), creation date, or alphabetical title.
- **🎨 Modern UI/UX**:
  - Dual Tailwind CSS utilities + Bootstrap 5 modal & toast architecture.
  - Collapsible, mobile-responsive sidebar with backdrop overlay.
  - Priority color ribbons and custom status tags.
  - Non-blocking asynchronous interactions (modal edits, quick-toggle status, delete confirmation).
- **🔒 Production-Ready Backend**:
  - SQLAlchemy ORM models with automatic timezone-aware UTC timestamps.
  - Input validation for required fields, character boundaries, and ISO date formatting.
  - RESTful JSON API endpoints supporting both web views and headless integrations.
  - Automated initial sample dataset generator on first boot.

---

## 📁 Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI automated pipeline
├── instance/                  # Local SQLite database directory (git-ignored)
├── static/
│   ├── css/
│   │   └── style.css          # Priority badges, status pills & custom UI transitions
│   └── js/
│       ├── app.js             # Client-side CRUD, Bootstrap modals & toast system
│       └── charts.js          # Chart.js visualization engine
├── templates/
│   ├── base.html              # Core layout shell, sidebar, modals & toasts
│   ├── dashboard.html         # Analytics dashboard, metric cards & deadlines
│   └── tasks.html             # Filterable task management board
├── tests/
│   └── test_app.py            # Automated unit test suite
├── .env.example               # Environment variables template
├── .gitignore                 # Production-grade git ignore rules
├── app.py                     # Flask application factory, web routes & REST API
├── LICENSE                    # MIT open-source license
├── models.py                  # SQLAlchemy Task model & JSON serialization
├── README.md                  # Project documentation & reference
└── requirements.txt           # Python package dependencies
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2. Set Up Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)
Copy the sample environment file if you wish to customize port or database URL:
```bash
# On Windows:
copy .env.example .env

# On Linux/macOS:
cp .env.example .env
```

### 5. Run the Application
```bash
python app.py
```

Visit **`http://127.0.0.1:5000`** in your browser. The app will automatically initialize the database and seed it with demo tasks.

---

## 🧪 Running Automated Tests

Run the included unit test suite using Python's built-in `unittest` runner:

```bash
python -m unittest discover tests
```

---

## 🔌 REST API Reference

The application exposes a clean RESTful API:

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/api/tasks` | Retrieve all tasks (supports query params `?status=`, `?priority=`, `?q=`) |
| `GET` | `/api/tasks/<id>` | Retrieve a single task by ID |
| `POST` | `/api/tasks` | Create a new task (`title`, `description`, `priority`, `status`, `due_date`) |
| `PUT` | `/api/tasks/<id>` | Update an existing task |
| `PATCH` | `/api/tasks/<id>/status` | Quick-update only the task status (`Pending`, `In Progress`, `Completed`) |
| `DELETE`| `/api/tasks/<id>` | Permanently delete a task |
| `GET` | `/api/statistics` | Retrieve dashboard metrics and priority/status counts |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is open-source and licensed under the [MIT License](LICENSE).
