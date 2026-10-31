import os
from datetime import datetime, date, timedelta, timezone
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from models import db, Task

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-task-manager-2026')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(base_dir, 'instance', 'tasks.db')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config:
        app.config.update(test_config)

    # Ensure instance directory exists
    os.makedirs(os.path.join(base_dir, 'instance'), exist_ok=True)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_initial_data_if_empty()

    # =========================================================================
    # Validation Helpers
    # =========================================================================
    VALID_PRIORITIES = {'Low', 'Medium', 'High', 'Urgent'}
    VALID_STATUSES = {'Pending', 'In Progress', 'Completed'}

    def validate_task_payload(data):
        errors = []
        title = data.get('title', '').strip()
        if not title:
            errors.append("Task title is required.")
        elif len(title) > 150:
            errors.append("Task title must be 150 characters or less.")

        priority = data.get('priority', 'Medium')
        if priority not in VALID_PRIORITIES:
            errors.append(f"Invalid priority '{priority}'. Allowed values: {', '.join(VALID_PRIORITIES)}.")

        status = data.get('status', 'Pending')
        if status not in VALID_STATUSES:
            errors.append(f"Invalid status '{status}'. Allowed values: {', '.join(VALID_STATUSES)}.")

        due_date_str = data.get('due_date')
        parsed_due_date = None
        if due_date_str:
            try:
                parsed_due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append("Invalid due date format. Must be YYYY-MM-DD.")

        return errors, {
            'title': title,
            'description': data.get('description', '').strip(),
            'priority': priority,
            'status': status,
            'due_date': parsed_due_date
        }

    # =========================================================================
    # Page Routes (HTML Views)
    # =========================================================================
    @app.route('/')
    def index():
        return redirect(url_for('dashboard'))

    @app.route('/dashboard')
    def dashboard():
        stats = get_dashboard_metrics()
        recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
        upcoming_tasks = Task.query.filter(
            Task.status != 'Completed',
            Task.due_date.isnot(None)
        ).order_by(Task.due_date.asc()).limit(5).all()

        return render_template(
            'dashboard.html',
            stats=stats,
            recent_tasks=recent_tasks,
            upcoming_tasks=upcoming_tasks
        )

    @app.route('/tasks')
    def tasks_page():
        status_filter = request.args.get('status', '').strip()
        priority_filter = request.args.get('priority', '').strip()
        search_query = request.args.get('q', '').strip()
        sort_by = request.args.get('sort', 'due_date')

        query = Task.query

        if status_filter and status_filter in VALID_STATUSES:
            query = query.filter(Task.status == status_filter)
        elif status_filter == 'Overdue':
            query = query.filter(
                Task.status != 'Completed',
                Task.due_date.isnot(None),
                Task.due_date < date.today()
            )

        if priority_filter and priority_filter in VALID_PRIORITIES:
            query = query.filter(Task.priority == priority_filter)

        if search_query:
            query = query.filter(
                (Task.title.ilike(f'%{search_query}%')) |
                (Task.description.ilike(f'%{search_query}%'))
            )

        # Sorting logic
        if sort_by == 'due_date':
            # Put nulls last
            query = query.order_by(Task.due_date.asc().nullslast())
        elif sort_by == 'due_date_desc':
            query = query.order_by(Task.due_date.desc().nullslast())
        elif sort_by == 'created_at':
            query = query.order_by(Task.created_at.desc())
        elif sort_by == 'title':
            query = query.order_by(Task.title.asc())

        task_list = query.all()
        return render_template(
            'tasks.html',
            tasks=task_list,
            status_filter=status_filter,
            priority_filter=priority_filter,
            search_query=search_query,
            sort_by=sort_by
        )

    # =========================================================================
    # REST API Endpoints (JSON for dynamic UI / AJAX)
    # =========================================================================
    @app.route('/api/tasks', methods=['GET'])
    def api_get_tasks():
        status = request.args.get('status')
        priority = request.args.get('priority')
        q = request.args.get('q')

        query = Task.query

        if status and status in VALID_STATUSES:
            query = query.filter(Task.status == status)
        elif status == 'Overdue':
            query = query.filter(
                Task.status != 'Completed',
                Task.due_date.isnot(None),
                Task.due_date < date.today()
            )

        if priority and priority in VALID_PRIORITIES:
            query = query.filter(Task.priority == priority)

        if q:
            query = query.filter(
                (Task.title.ilike(f'%{q}%')) |
                (Task.description.ilike(f'%{q}%'))
            )

        tasks = query.order_by(Task.created_at.desc()).all()
        return jsonify([t.to_dict() for t in tasks]), 200

    @app.route('/api/tasks/<int:task_id>', methods=['GET'])
    def api_get_task(task_id):
        task = db.get_or_404(Task, task_id)
        return jsonify(task.to_dict()), 200

    @app.route('/api/tasks', methods=['POST'])
    def api_create_task():
        data = request.get_json() or request.form.to_dict()
        errors, cleaned_data = validate_task_payload(data)
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        new_task = Task(
            title=cleaned_data['title'],
            description=cleaned_data['description'],
            priority=cleaned_data['priority'],
            status=cleaned_data['status'],
            due_date=cleaned_data['due_date']
        )
        db.session.add(new_task)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Task created successfully!',
            'task': new_task.to_dict()
        }), 201

    @app.route('/api/tasks/<int:task_id>', methods=['PUT', 'POST'])
    def api_update_task(task_id):
        task = db.get_or_404(Task, task_id)
        data = request.get_json() or request.form.to_dict()
        errors, cleaned_data = validate_task_payload(data)
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        task.title = cleaned_data['title']
        task.description = cleaned_data['description']
        task.priority = cleaned_data['priority']
        task.status = cleaned_data['status']
        task.due_date = cleaned_data['due_date']
        task.updated_at = datetime.now(timezone.utc)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Task updated successfully!',
            'task': task.to_dict()
        }), 200

    @app.route('/api/tasks/<int:task_id>/status', methods=['PATCH', 'POST'])
    def api_update_status(task_id):
        task = db.get_or_404(Task, task_id)
        data = request.get_json() or request.form.to_dict()
        new_status = data.get('status')
        if new_status not in VALID_STATUSES:
            return jsonify({'success': False, 'error': f"Invalid status '{new_status}'."}), 400

        task.status = new_status
        task.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f"Status updated to '{new_status}'.",
            'task': task.to_dict()
        }), 200

    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    def api_delete_task(task_id):
        task = db.get_or_404(Task, task_id)
        task_title = task.title
        db.session.delete(task)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f"Task '{task_title}' deleted successfully!"
        }), 200

    @app.route('/api/statistics', methods=['GET'])
    def api_statistics():
        stats = get_dashboard_metrics()
        return jsonify(stats), 200

    # Helper function to compute statistics
    def get_dashboard_metrics():
        total = Task.query.count()
        completed = Task.query.filter_by(status='Completed').count()
        in_progress = Task.query.filter_by(status='In Progress').count()
        pending = Task.query.filter_by(status='Pending').count()

        today = date.today()
        overdue = Task.query.filter(
            Task.status != 'Completed',
            Task.due_date.isnot(None),
            Task.due_date < today
        ).count()

        completion_rate = round((completed / total * 100), 1) if total > 0 else 0

        # Priority Counts
        priorities = {
            'Low': Task.query.filter_by(priority='Low').count(),
            'Medium': Task.query.filter_by(priority='Medium').count(),
            'High': Task.query.filter_by(priority='High').count(),
            'Urgent': Task.query.filter_by(priority='Urgent').count(),
        }

        # Status Counts
        statuses = {
            'Pending': pending,
            'In Progress': in_progress,
            'Completed': completed
        }

        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'in_progress_tasks': in_progress,
            'pending_tasks': pending,
            'overdue_tasks': overdue,
            'completion_rate': completion_rate,
            'priorities': priorities,
            'statuses': statuses
        }

    return app


def seed_initial_data_if_empty():
    if Task.query.count() == 0:
        today = date.today()
        sample_tasks = [
            Task(
                title="Design System & UI Components",
                description="Finalize color tokens, typography, and card components in Tailwind & Bootstrap.",
                priority="High",
                status="Completed",
                due_date=today - timedelta(days=2)
            ),
            Task(
                title="Database Migration & Schema Definition",
                description="Setup SQLite database models with SQLAlchemy and configure indexes.",
                priority="Urgent",
                status="Completed",
                due_date=today - timedelta(days=1)
            ),
            Task(
                title="Implement REST API Endpoints",
                description="Create CRUD routes for tasks with payload validation and error responses.",
                priority="High",
                status="In Progress",
                due_date=today + timedelta(days=1)
            ),
            Task(
                title="Build Interactive Dashboard & Charts",
                description="Integrate Chart.js metrics for priority and status distribution visualization.",
                priority="Medium",
                status="In Progress",
                due_date=today + timedelta(days=3)
            ),
            Task(
                title="Setup User Authentication Module",
                description="Research OAuth2 / session based authentication flow for team collaboration.",
                priority="Low",
                status="Pending",
                due_date=today + timedelta(days=7)
            ),
            Task(
                title="Review Quarterly Project Deliverables",
                description="Consolidate team task progress, metrics, and overdue item logs for stakeholder review.",
                priority="Urgent",
                status="Pending",
                due_date=today - timedelta(days=1)  # Intentionally overdue for demo
            ),
            Task(
                title="Optimize Client-side Asset Bundling",
                description="Minify custom stylesheet and script bundles for faster First Contentful Paint.",
                priority="Medium",
                status="Pending",
                due_date=today + timedelta(days=5)
            )
        ]
        for task in sample_tasks:
            db.session.add(task)
        db.session.commit()
        print("Database seeded with sample tasks successfully.")


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(debug=debug, host='0.0.0.0', port=port)
