from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  
    full_name = db.Column(db.String(255), nullable=True)
    qualification = db.Column(db.String(255), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    active = db.Column(db.Boolean(), default=True)
    role = db.Column(db.String(50), default='user')  

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship(
        'Chapter', backref='subject', lazy=True, cascade="all, delete-orphan"
    )

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    quizzes = db.relationship(
        'Quiz', backref='chapter', lazy=True, cascade="all, delete-orphan"
    )

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, default=datetime.utcnow)
    time_duration = db.Column(db.Integer)  
    remarks = db.Column(db.Text)
    questions = db.relationship(
        'Question', backref='quiz', lazy=True, cascade="all, delete-orphan"
    )
    scores = db.relationship(
        'Score', backref='quiz', lazy=True, cascade="all, delete-orphan"
    )

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    options = db.relationship(
        'Option', backref='question', lazy=True, cascade="all, delete-orphan"
    )

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_scored = db.Column(db.Float, default=0.0)
    user_answers = db.relationship('UserAnswer', backref='score', lazy=True, cascade="all, delete-orphan")


class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score_id = db.Column(db.Integer, db.ForeignKey('score.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('option.id'), nullable=False)

