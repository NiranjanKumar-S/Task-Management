import unittest
from app import create_app
from models import db, Task

class TaskFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_dashboard_page(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard Overview', response.data)

    def test_tasks_page(self):
        response = self.client.get('/tasks')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Tasks Management', response.data)

    def test_create_and_delete_task_api(self):
        # 1. Create task
        res_create = self.client.post('/api/tasks', json={
            'title': 'Test Repository Unit Test',
            'description': 'Automated test task',
            'priority': 'High',
            'status': 'Pending',
            'due_date': '2026-12-31'
        })
        self.assertEqual(res_create.status_code, 201)
        data = res_create.get_json()
        self.assertTrue(data['success'])
        task_id = data['task']['id']

        # 2. Get task
        res_get = self.client.get(f'/api/tasks/{task_id}')
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(res_get.get_json()['title'], 'Test Repository Unit Test')

        # 3. Update status
        res_status = self.client.patch(f'/api/tasks/{task_id}/status', json={'status': 'Completed'})
        self.assertEqual(res_status.status_code, 200)
        self.assertEqual(res_status.get_json()['task']['status'], 'Completed')

        # 4. Delete task
        res_delete = self.client.delete(f'/api/tasks/{task_id}')
        self.assertEqual(res_delete.status_code, 200)

        # 5. Verify deleted
        res_deleted = self.client.get(f'/api/tasks/{task_id}')
        self.assertEqual(res_deleted.status_code, 404)

    def test_validation_error(self):
        # Empty title should return 400
        res = self.client.post('/api/tasks', json={
            'title': '',
            'priority': 'InvalidPriority'
        })
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.get_json()['success'])

if __name__ == '__main__':
    unittest.main()
