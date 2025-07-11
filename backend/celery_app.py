from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta

from app import app 
from models import db, User, Score, Quiz  
from mail import send_mail  

import csv
import os


celery = Celery(
    'celery_app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'  
)

celery.conf.update(
    timezone='Asia/Kolkata',
    enable_utc=False,
)


@celery.task()
def generate_csv_export(user_id):
    """
    Generate a CSV of all quizzes attempted by a user and email it.
    """
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return f"No user found with ID {user_id}"

        scores = Score.query.filter_by(user_id=user_id).all()
        if not scores:
            return "No quiz attempts found for user."

       
        filename = f'user_{user_id}_quiz_export.csv'
        filepath = os.path.join('static', filename)

        
        os.makedirs('static', exist_ok=True)

      
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['score_id', 'quiz_id', 'quiz_date', 'total_scored', 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for score in scores:
                quiz = Quiz.query.get(score.quiz_id)
                writer.writerow({
                    'score_id': score.id,
                    'quiz_id': score.quiz_id,
                    'quiz_date': quiz.date_of_quiz.isoformat() if quiz and quiz.date_of_quiz else '',
                    'total_scored': score.total_scored,
                    'timestamp': score.timestamp.isoformat() if score.timestamp else ''
                })

        
        body = (
            f"Hello {user.full_name},\n\n"
            f"Your quiz export CSV is ready. Download it here:\n"
            f"http://127.0.0.1:5000/static/{filename}\n\n"
            f"Regards,\nQuiz Master Team"
        )

        send_mail(user.email, "Your Quiz Export CSV is Ready", body)
        return f"CSV generated and email sent to {user.email}"


@celery.task()
def daily_reminder_emails():
    """
    Send daily reminders to users who have not attempted any quiz in the last 7 days.
    """
    with app.app_context():
        users = User.query.filter(User.role != 'admin').all()
        now = datetime.utcnow()
        cutoff = now - timedelta(days=7)

        for user in users:
            last_score = Score.query.filter_by(user_id=user.id).order_by(Score.timestamp.desc()).first()

            if not last_score or last_score.timestamp < cutoff:
                body = (
                    f"Hello {user.full_name},\n\n"
                    f"We noticed you haven't attempted any quizzes in the last week.\n"
                    f"Visit Quiz Master and keep practicing your skills!\n"
                    f"http://127.0.0.1:5173/\n\n"
                    f"Best regards,\nQuiz Master Team"
                )
                send_mail(user.email, "Reminder: Come Back to Quiz Master!", body)

        return "Daily reminders sent."


from celery import Celery
from celery.schedules import crontab

celery = Celery('celery_app')
celery.conf.broker_url = 'redis://localhost:6379/0'
celery.conf.result_backend = 'redis://localhost:6379/0'

@celery.task()
def monthly_activity_report():
    """
    Send monthly activity reports with quiz stats to all users.
    """
    with app.app_context():
        users = User.query.filter(User.role != 'admin').all()
        now = datetime.utcnow()
        first_day_last_month = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = now.replace(day=1) - timedelta(days=1)

        for user in users:
            scores = Score.query.filter(
                Score.user_id == user.id,
                Score.timestamp >= first_day_last_month,
                Score.timestamp <= last_day_last_month
            ).all()

            quiz_count = len(scores)
            avg_score = sum(s.total_scored for s in scores) / quiz_count if quiz_count > 0 else 0

            body = (
                f"Hello {user.full_name},\n\n"
                f"Here is your activity report for {first_day_last_month.strftime('%B %Y')}:\n"
                f"Total quizzes taken: {quiz_count}\n"
                f"Average score: {avg_score:.2f}%\n\n"
                f"Keep up the great work!\n\n"
                f"Regards,\nQuiz Master Team"
            )
            send_mail(user.email, f"Your Monthly Quiz Activity Report - {first_day_last_month.strftime('%B %Y')}", body)

        return "Monthly reports sent."





celery.conf.beat_schedule = {
    'send_daily_reminders': {
        'task': 'celery_app.daily_reminder_emails',
        'schedule': crontab(minute='*/1'), 
    },
    'send_monthly_reports': {
        'task': 'celery_app.monthly_activity_report',
        'schedule': crontab(minute='*/1'),  
    },
}
