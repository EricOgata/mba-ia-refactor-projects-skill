"""Agregações e relatórios — regra de negócio, sem HTTP."""

from datetime import timedelta

from errors import NotFoundError
from repositories.category_repository import CategoryRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from utils.helpers import calculate_percentage, utcnow


class ReportService:
    def __init__(self, task_repo=None, user_repo=None, category_repo=None):
        self.tasks = task_repo or TaskRepository()
        self.users = user_repo or UserRepository()
        self.categories = category_repo or CategoryRepository()

    def summary(self):
        now = utcnow()
        by_status = self.tasks.count_by_status()
        by_priority = self.tasks.count_by_priority()
        overdue = self.tasks.get_overdue(now)
        seven_days_ago = now - timedelta(days=7)

        user_stats = []
        totals, completed = self.tasks.productivity_by_user()
        for user in self.users.get_all():
            total = totals.get(user.id, 0)
            done = completed.get(user.id, 0)
            user_stats.append({
                'user_id': user.id,
                'user_name': user.name,
                'total_tasks': total,
                'completed_tasks': done,
                'completion_rate': calculate_percentage(done, total),
            })

        return {
            'generated_at': str(now),
            'overview': {
                'total_tasks': sum(by_status.values()),
                'total_users': self.users.count(),
                'total_categories': self.categories.count(),
            },
            'tasks_by_status': {
                'pending': by_status['pending'],
                'in_progress': by_status['in_progress'],
                'done': by_status['done'],
                'cancelled': by_status['cancelled'],
            },
            'tasks_by_priority': {
                'critical': by_priority.get(1, 0),
                'high': by_priority.get(2, 0),
                'medium': by_priority.get(3, 0),
                'low': by_priority.get(4, 0),
                'minimal': by_priority.get(5, 0),
            },
            'overdue': {
                'count': len(overdue),
                'tasks': [
                    {
                        'id': task.id,
                        'title': task.title,
                        'due_date': str(task.due_date),
                        'days_overdue': (now - task.due_date).days,
                    }
                    for task in overdue
                ],
            },
            'recent_activity': {
                'tasks_created_last_7_days': self.tasks.count_created_since(seven_days_ago),
                'tasks_completed_last_7_days': self.tasks.count_completed_since(seven_days_ago),
            },
            'user_productivity': user_stats,
        }

    def user_report(self, user_id):
        user = self.users.get_by_id(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')

        tasks = self.tasks.get_by_user(user_id)
        total = len(tasks)
        done = sum(1 for task in tasks if task.status == 'done')
        pending = sum(1 for task in tasks if task.status == 'pending')
        in_progress = sum(1 for task in tasks if task.status == 'in_progress')
        cancelled = sum(1 for task in tasks if task.status == 'cancelled')
        overdue = sum(1 for task in tasks if task.is_overdue())
        high_priority = sum(1 for task in tasks if task.priority <= 2)

        return {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            },
            'statistics': {
                'total_tasks': total,
                'done': done,
                'pending': pending,
                'in_progress': in_progress,
                'cancelled': cancelled,
                'overdue': overdue,
                'high_priority': high_priority,
                'completion_rate': calculate_percentage(done, total),
            },
        }
