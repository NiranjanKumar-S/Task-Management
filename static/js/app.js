/**
 * TaskFlow Application JavaScript
 * Handles CRUD operations, Bootstrap Modals, API calls, and Toast notifications.
 */

// Global Modal & Toast instances
let taskModalInstance = null;
let deleteModalInstance = null;
let toastInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Bootstrap Modals
    const taskModalEl = document.getElementById('taskModal');
    if (taskModalEl) {
        taskModalInstance = new bootstrap.Modal(taskModalEl);
    }

    const deleteModalEl = document.getElementById('deleteConfirmModal');
    if (deleteModalEl) {
        deleteModalInstance = new bootstrap.Modal(deleteModalEl);
    }

    const toastEl = document.getElementById('liveToast');
    if (toastEl) {
        toastInstance = new bootstrap.Toast(toastEl, { delay: 4000 });
    }

    // Initialize Mobile Sidebar
    setupMobileSidebar();

    // Setup Form Submissions & Listeners
    setupTaskForm();
    setupDeleteConfirmation();
});

/* =========================================================================
   Sidebar Mobile Navigation
   ========================================================================= */
function setupMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    const openBtn = document.getElementById('openSidebarBtn');
    const closeBtn = document.getElementById('closeSidebarBtn');

    if (!sidebar || !backdrop) return;

    function openSidebar() {
        sidebar.classList.remove('-translate-x-full');
        backdrop.classList.remove('hidden');
    }

    function closeSidebar() {
        sidebar.classList.add('-translate-x-full');
        backdrop.classList.add('hidden');
    }

    if (openBtn) openBtn.addEventListener('click', openSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    backdrop.addEventListener('click', closeSidebar);
}

/* =========================================================================
   Toast Notifications
   ========================================================================= */
function showToast(message, type = 'success') {
    const toastEl = document.getElementById('liveToast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');

    if (!toastEl || !toastInstance) return;

    // Reset background classes
    toastEl.className = 'toast align-items-center text-white border-0 shadow-xl rounded-xl';

    if (type === 'success') {
        toastEl.classList.add('bg-emerald-600');
        toastIcon.className = 'bi bi-check-circle-fill text-lg text-white';
    } else if (type === 'error') {
        toastEl.classList.add('bg-rose-600');
        toastIcon.className = 'bi bi-x-circle-fill text-lg text-white';
    } else {
        toastEl.classList.add('bg-indigo-600');
        toastIcon.className = 'bi bi-info-circle-fill text-lg text-white';
    }

    toastMessage.textContent = message;
    toastInstance.show();
}

/* =========================================================================
   Create & Edit Task Modal Handlers
   ========================================================================= */
function openCreateTaskModal() {
    const form = document.getElementById('taskForm');
    if (!form) return;

    form.reset();
    document.getElementById('taskId').value = '';
    document.getElementById('taskModalLabel').textContent = 'Create New Task';
    document.getElementById('taskModalIcon').className = 'bi bi-plus-lg';
    document.getElementById('saveBtnText').textContent = 'Create Task';
    
    // Clear error alert
    const alertBox = document.getElementById('modalAlert');
    alertBox.classList.add('hidden');
    alertBox.innerHTML = '';

    // Set default status & priority
    document.getElementById('taskPriority').value = 'Medium';
    document.getElementById('taskStatus').value = 'Pending';

    taskModalInstance.show();
}

async function openEditTaskModal(taskId) {
    const alertBox = document.getElementById('modalAlert');
    alertBox.classList.add('hidden');
    alertBox.innerHTML = '';

    try {
        const response = await fetch(`/api/tasks/${taskId}`);
        if (!response.ok) throw new Error('Failed to load task details');

        const task = await response.json();

        document.getElementById('taskId').value = task.id;
        document.getElementById('taskTitle').value = task.title;
        document.getElementById('taskDescription').value = task.description || '';
        document.getElementById('taskPriority').value = task.priority;
        document.getElementById('taskStatus').value = task.status;
        document.getElementById('taskDueDate').value = task.due_date || '';

        document.getElementById('taskModalLabel').textContent = 'Edit Task';
        document.getElementById('taskModalIcon').className = 'bi bi-pencil-square';
        document.getElementById('saveBtnText').textContent = 'Update Task';

        taskModalInstance.show();
    } catch (error) {
        showToast('Error loading task details: ' + error.message, 'error');
    }
}

/* =========================================================================
   Form Submission (AJAX POST / PUT)
   ========================================================================= */
function setupTaskForm() {
    const form = document.getElementById('taskForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const taskId = document.getElementById('taskId').value;
        const title = document.getElementById('taskTitle').value.trim();
        const description = document.getElementById('taskDescription').value.trim();
        const priority = document.getElementById('taskPriority').value;
        const status = document.getElementById('taskStatus').value;
        const dueDate = document.getElementById('taskDueDate').value;

        const alertBox = document.getElementById('modalAlert');
        const spinner = document.getElementById('saveBtnSpinner');
        const saveBtn = document.getElementById('saveTaskBtn');

        // Basic front-end validation
        if (!title) {
            alertBox.textContent = 'Please enter a task title.';
            alertBox.classList.remove('hidden');
            return;
        }

        const payload = {
            title: title,
            description: description,
            priority: priority,
            status: status,
            due_date: dueDate || null
        };

        // UI Loading state
        spinner.classList.remove('hidden');
        saveBtn.disabled = true;
        alertBox.classList.add('hidden');

        try {
            const isEdit = Boolean(taskId);
            const url = isEdit ? `/api/tasks/${taskId}` : '/api/tasks';
            const method = isEdit ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                const errors = data.errors ? data.errors.join('<br>') : (data.error || 'Failed to save task.');
                alertBox.innerHTML = errors;
                alertBox.classList.remove('hidden');
                return;
            }

            // Success
            taskModalInstance.hide();
            showToast(data.message || (isEdit ? 'Task updated!' : 'Task created!'), 'success');

            // Refresh the current view to reflect state cleanly
            setTimeout(() => {
                window.location.reload();
            }, 600);

        } catch (error) {
            alertBox.textContent = 'An unexpected error occurred: ' + error.message;
            alertBox.classList.remove('hidden');
        } finally {
            spinner.classList.add('hidden');
            saveBtn.disabled = false;
        }
    });
}

/* =========================================================================
   Delete Task Confirmation
   ========================================================================= */
function confirmDeleteTask(taskId, taskTitle) {
    document.getElementById('deleteTaskId').value = taskId;
    document.getElementById('deleteTaskTitle').textContent = `"${taskTitle}"`;
    deleteModalInstance.show();
}

function setupDeleteConfirmation() {
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    if (!confirmBtn) return;

    confirmBtn.addEventListener('click', async () => {
        const taskId = document.getElementById('deleteTaskId').value;
        const spinner = document.getElementById('deleteSpinner');

        if (!taskId) return;

        spinner.classList.remove('hidden');
        confirmBtn.disabled = true;

        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to delete task.');
            }

            deleteModalInstance.hide();
            showToast(data.message || 'Task deleted successfully.', 'success');

            // Remove card or reload
            const cardEl = document.getElementById(`task-card-${taskId}`);
            if (cardEl) {
                cardEl.style.transition = 'all 0.3s ease';
                cardEl.style.opacity = '0';
                cardEl.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    cardEl.remove();
                    window.location.reload();
                }, 300);
            } else {
                setTimeout(() => window.location.reload(), 500);
            }

        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            spinner.classList.add('hidden');
            confirmBtn.disabled = false;
        }
    });
}

/* =========================================================================
   Quick Status Update (Inline button / dropdown toggle)
   ========================================================================= */
async function quickUpdateStatus(taskId, newStatus) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to update status.');
        }

        showToast(`Task status updated to "${newStatus}"`, 'success');
        setTimeout(() => {
            window.location.reload();
        }, 500);

    } catch (error) {
        showToast('Error updating status: ' + error.message, 'error');
    }
}
