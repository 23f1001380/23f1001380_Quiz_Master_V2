from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
)
from cache import cache
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from models import db, User, Subject, Chapter, Quiz, Question, Option, Score, UserAnswer

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'

db.init_app(app)
cache.init_app(app) 

CORS(app, origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5000",
    "http://127.0.0.1:5000"
], supports_credentials=True)

jwt = JWTManager(app)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 200
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'msg': 'Admins only!'}), 403
        return fn(*args, **kwargs)
    return wrapper

def setup_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email="admin@gmail.com").first():
            db.session.add(User(
                email="admin@gmail.com",
                password=generate_password_hash("admin123"),
                full_name="Admin",
                qualification="NA",
                role="admin"
            ))
            db.session.commit()



@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'msg': 'Invalid credentials'}), 401
    token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})

    return jsonify({'user_id': user.id, 'token': token, 'role': user.role}), 200

@app.route('/api/auth/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name', '')
    qualification = data.get('qualification', '')
    if not email or not password:
        return jsonify({'msg': 'Email and password are required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'Email already exists'}), 409
    hashed_pw = generate_password_hash(password)
    user = User(email=email, password=hashed_pw, full_name=full_name,
                qualification=qualification, role='user')
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'Signup successful!'}), 201


@app.route('/api/admin/subjects', methods=['GET', 'OPTIONS'])
@jwt_required()
@admin_required
#@cache.cached(timeout=20, key_prefix='admin_subjects')  # Cache for 5 minutes
def get_subjects():
    if request.method == 'OPTIONS':
        return '', 200
    subjects = Subject.query.all()
    return jsonify([
        {'id': s.id, 'name': s.name, 'description': s.description}
        for s in subjects
    ])

@app.route('/api/admin/subjects', methods=['POST'])
@jwt_required()
@admin_required
def post_subject():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    if not name or not name.strip():
        return jsonify({'msg': 'Subject name required'}), 400
    subject = Subject(name=name, description=description)
    db.session.add(subject)
    db.session.commit()
    
   
    cache.delete('flask_cache_admin_subjects')
    
    return jsonify({'msg': 'Subject added', 'id': subject.id}), 201


@app.route('/api/admin/subjects/<int:subject_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@jwt_required()
@admin_required
def subject_update_delete(subject_id):
    if request.method == 'OPTIONS':
        return '', 200

    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({'msg': 'Subject not found'}), 404

    if request.method == 'PUT':
        data = request.get_json()
        subject.name = data.get('name', subject.name)
        subject.description = data.get('description', subject.description)
        db.session.commit()
        
        
        cache.delete('flask_cache_admin_subjects')
        
        return jsonify({'msg': 'Subject updated'})

    elif request.method == 'DELETE':
        db.session.delete(subject)
        db.session.commit()
        
        
        cache.delete('flask_cache_admin_subjects')
        
        return jsonify({'msg': 'Subject deleted'})

@app.route('/api/admin/chapters', methods=['POST', 'OPTIONS'])
@jwt_required()
@admin_required
def create_chapter():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    subject_id = data.get('subject_id')

    if not name or not subject_id:
        return jsonify({'msg': 'Chapter name and subject_id required'}), 400

    chapter = Chapter(name=name, description=description, subject_id=subject_id)
    db.session.add(chapter)
    db.session.commit()
    return jsonify({'msg': 'Chapter created', 'id': chapter.id}), 201

@app.route('/api/admin/chapters', methods=['GET', 'OPTIONS'])
@jwt_required()
@admin_required
def get_all_chapters():
    if request.method == 'OPTIONS':
        return '', 200

    chapters = Chapter.query.all()
    return jsonify([
        {
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'subject_id': c.subject_id,
            'subject_name': c.subject.name if c.subject else ""
        }
        for c in chapters
    ])



@app.route('/api/admin/chapters/<int:chapter_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@jwt_required()
@admin_required
def chapter_update_delete(chapter_id):
    if request.method == 'OPTIONS':
        return '', 200
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return jsonify({'msg': 'Chapter not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        chapter.name = data.get('name', chapter.name)
        chapter.description = data.get('description', chapter.description)
        chapter.subject_id = data.get('subject_id', chapter.subject_id)
        db.session.commit()
        return jsonify({'msg': 'Chapter updated'})
    elif request.method == 'DELETE':
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({'msg': 'Chapter deleted'})


from datetime import datetime

@app.route('/api/admin/quizzes', methods=['GET', 'POST', 'OPTIONS'])
@jwt_required()
@admin_required
def quizzes_handler():
    if request.method == 'OPTIONS':
        return '', 200

    if request.method == 'GET':
        quizzes = Quiz.query.all()
        return jsonify([
            {
                'id': q.id,
                'date_of_quiz': q.date_of_quiz.isoformat() if q.date_of_quiz else None,
                'time_duration': q.time_duration,
                'remarks': q.remarks,
                'chapter_id': q.chapter_id,
                'chapter_name': q.chapter.name if hasattr(q, 'chapter') and q.chapter else ""
            }
            for q in quizzes
        ])

    elif request.method == 'POST':
        data = request.get_json()
        chapter_id = data.get('chapter_id')
        date_of_quiz_str = data.get('date_of_quiz')
        time_duration = data.get('time_duration')
        remarks = data.get('remarks', '')

        
        if not chapter_id or not date_of_quiz_str or not time_duration:
            return jsonify({'msg': 'Missing required fields'}), 400

        
        try:
            
            if date_of_quiz_str and len(date_of_quiz_str) == 10:
               
                date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d")
            else:
               
                if date_of_quiz_str and len(date_of_quiz_str) == 16:
                    date_of_quiz_str += ":00"  # Add seconds if missing
                date_of_quiz = datetime.fromisoformat(date_of_quiz_str)
        except Exception as e:
            return jsonify({'msg': f'Invalid date format: {e}'}), 400

        quiz = Quiz(
            chapter_id=chapter_id,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks
        )
        db.session.add(quiz)
        db.session.commit()
        return jsonify({'msg': 'Quiz added', 'id': quiz.id}), 201

@app.route('/api/admin/quizzes/<int:quiz_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@jwt_required()
@admin_required
def quiz_update_delete(quiz_id):
    if request.method == 'OPTIONS':
        return '', 200

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'msg': 'Quiz not found'}), 404

    if request.method == 'PUT':
        data = request.get_json()
        if 'chapter_id' in data:
            quiz.chapter_id = data['chapter_id']
        if 'date_of_quiz' in data:
            date_of_quiz_str = data['date_of_quiz']
            try:
                if date_of_quiz_str and len(date_of_quiz_str) == 10:
                    quiz.date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d")
                else:
                    if date_of_quiz_str and len(date_of_quiz_str) == 16:
                        date_of_quiz_str += ":00"
                    quiz.date_of_quiz = datetime.fromisoformat(date_of_quiz_str)
            except Exception as e:
                return jsonify({'msg': f'Invalid date format: {e}'}), 400
        if 'time_duration' in data:
            quiz.time_duration = data['time_duration']
        if 'remarks' in data:
            quiz.remarks = data['remarks']
        db.session.commit()
        return jsonify({'msg': 'Quiz updated'})

    elif request.method == 'DELETE':
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({'msg': 'Quiz deleted'})




@app.route('/api/admin/questions', methods=['GET', 'POST', 'OPTIONS'])
@jwt_required()
@admin_required
def questions_handler():
    if request.method == 'OPTIONS':
        return '', 200

    if request.method == 'GET':
        questions = Question.query.all()
        return jsonify([
            {
                'id': q.id,
                'quiz_id': q.quiz_id,
                'question_statement': q.question_statement,
                'quiz_name': q.quiz.remarks if q.quiz else "",
            }
            for q in questions
        ])

    elif request.method == 'POST':
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        question_statement = data.get('question_statement')
        if not quiz_id or not question_statement or not question_statement.strip():
            return jsonify({'msg': 'quiz_id and question_statement required'}), 400
        question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement
        )
        db.session.add(question)
        db.session.commit()
        return jsonify({'msg': 'Question added', 'id': question.id}), 201

@app.route('/api/admin/questions/<int:question_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@jwt_required()
@admin_required
def question_update_delete(question_id):
    if request.method == 'OPTIONS':
        return '', 200

    question = Question.query.get(question_id)
    if not question:
        return jsonify({'msg': 'Question not found'}), 404

    if request.method == 'PUT':
        data = request.get_json()
        question.quiz_id = data.get('quiz_id', question.quiz_id)
        question.question_statement = data.get('question_statement', question.question_statement)
        db.session.commit()
        return jsonify({'msg': 'Question updated'})

    elif request.method == 'DELETE':
        db.session.delete(question)
        db.session.commit()
        return jsonify({'msg': 'Question deleted'})






@app.route('/api/admin/options', methods=['GET', 'POST', 'OPTIONS'])
@jwt_required()
@admin_required
def options_handler():
    if request.method == 'OPTIONS':
        return '', 200
    if request.method == 'GET':
        question_id = request.args.get('question_id')
        query = Option.query
        if question_id:
            query = query.filter_by(question_id=question_id)
        options = query.all()
        return jsonify([
            {
                'id': o.id,
                'question_id': o.question_id,
                'text': o.text,
                'is_correct': o.is_correct
            }
            for o in options
        ])
    elif request.method == 'POST':
        data = request.get_json()
        question_id = data.get('question_id')
        text = data.get('text')
        is_correct = data.get('is_correct', False)
        if not question_id or not text:
            return jsonify({'msg': 'Question ID and text are required'}), 400
        option = Option(
            question_id=question_id,
            text=text,
            is_correct=bool(is_correct)
        )
        db.session.add(option)
        db.session.commit()
        return jsonify({'msg': 'Option added', 'id': option.id}), 201

@app.route('/api/admin/options/<int:option_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@jwt_required()
@admin_required
def option_update_delete(option_id):
    if request.method == 'OPTIONS':
        return '', 200
    option = Option.query.get(option_id)
    if not option:
        return jsonify({'msg': 'Option not found'}), 404
    if request.method == 'PUT':
        data = request.get_json()
        option.text = data.get('text', option.text)
        option.is_correct = data.get('is_correct', option.is_correct)
        db.session.commit()
        return jsonify({'msg': 'Option updated'})
    elif request.method == 'DELETE':
        db.session.delete(option)
        db.session.commit()
        return jsonify({'msg': 'Option deleted'})


@app.route('/api/user/dashboard', methods=['GET', 'OPTIONS'])
@jwt_required()
def user_dashboard():
    if request.method == 'OPTIONS':
        return '', 200
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    return jsonify({
        'user_id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'qualification': user.qualification,
        'role': user.role
    }), 200


@app.route('/api/user/subjects', methods=['GET', 'OPTIONS'])
@jwt_required()

def user_subjects():
    if request.method == 'OPTIONS':
        return '', 200
    subjects = Subject.query.all()
    return jsonify([
        {'id': s.id, 'name': s.name, 'description': s.description}
        for s in subjects
    ])


@app.route('/api/user/chapters/<int:subject_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def user_chapters(subject_id):
    if request.method == 'OPTIONS':
        return '', 200
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify([
        {
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'subject_id': c.subject_id,
            'subject_name': c.subject.name if c.subject else ""
        }
        for c in chapters
    ])


@app.route('/api/user/quizzes/<int:chapter_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def user_quizzes(chapter_id):
    if request.method == 'OPTIONS':
        return '', 200
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return jsonify([
        {
            'id': q.id,
            'date_of_quiz': q.date_of_quiz.isoformat() if q.date_of_quiz else None,
            'time_duration': q.time_duration,
            'remarks': q.remarks,
            'chapter_id': q.chapter_id,
            'chapter_name': q.chapter.name if q.chapter else ""
        }
        for q in quizzes
    ])

@app.route('/api/user/questions/<int:quiz_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def user_questions(quiz_id):
    if request.method == 'OPTIONS':
        return '', 200
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    results = []
    for q in questions:
        options = Option.query.filter_by(question_id=q.id).all()
        results.append({
            'id': q.id,
            'quiz_id': q.quiz_id,
            'question_statement': q.question_statement,
            'options': [
                {
                    'id': o.id,
                    'text': o.text,
                    
                } for o in options
            ]
        })
    return jsonify(results)


@app.route('/api/user/submit_quiz', methods=['POST', 'OPTIONS'])
@jwt_required()
def user_submit_quiz():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    quiz_id = data.get('quiz_id')
    answers = data.get('answers', []) 
    user_id = get_jwt_identity()

    if not quiz_id:
        return jsonify({'msg': 'quiz_id required'}), 400
    if answers is None:
        return jsonify({'msg': 'answers required'}), 400

    
    total_questions = 0
    total_correct = 0

    
    score = Score(
        quiz_id=quiz_id,
        user_id=user_id,
        timestamp=datetime.utcnow(),
        total_scored=0.0 
    )
    db.session.add(score)
    db.session.flush()  

    for answer in answers:
        question_id = answer.get('question_id')
        selected_option_id = answer.get('selected_option_id')
        if not question_id or not selected_option_id:
            continue
        option = Option.query.filter_by(id=selected_option_id, question_id=question_id).first()
        if option and option.is_correct:
            total_correct += 1
        total_questions += 1
        user_answer = UserAnswer(
            score_id=score.id,
            question_id=question_id,
            selected_option_id=selected_option_id
        )
        db.session.add(user_answer)

   
    if total_questions > 0:
        score.total_scored = (total_correct / total_questions) * 100
    else:
        score.total_scored = 0

    db.session.commit()

    return jsonify({
        'msg': 'Quiz submitted successfully!',
        'quiz_id': quiz_id,
        'total_questions': total_questions,
        'correct_answers': total_correct,
        'score': score.total_scored
    }), 200


@app.route('/api/user/scores', methods=['GET', 'OPTIONS'])
@jwt_required()
def user_scores():
    if request.method == 'OPTIONS':
        return '', 200
    user_id = get_jwt_identity()
    scores = Score.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            'id': s.id,
            'quiz_id': s.quiz_id,
            'timestamp': s.timestamp.isoformat() if s.timestamp else "",
            'total_scored': s.total_scored,
        }
        for s in scores
    ])


@app.route('/api/user/score_details/<int:score_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def user_score_details(score_id):
    if request.method == 'OPTIONS':
        return '', 200
    user_id = get_jwt_identity()
    score = Score.query.filter_by(id=score_id, user_id=user_id).first()
    if not score:
        return jsonify({'msg': 'Not found'}), 404
    
    answers = []
    for ua in score.answers: 
        q = ua.question
        options = Option.query.filter_by(question_id=q.id).all()
        answers.append({
            'question_id': q.id,
            'question_statement': q.question_statement,
            'selected_option_id': ua.selected_option_id,
            'options': [{'id': o.id, 'text': o.text, 'is_correct': o.is_correct} for o in options]
        })
    return jsonify({
        'score_id': score.id,
        'quiz_id': score.quiz_id,
        'timestamp': score.timestamp.isoformat() if score.timestamp else "",
        'total_scored': score.total_scored,
        'answers': answers
    })


@app.route('/api/user/export_quiz_csv', methods=['POST', 'OPTIONS'])
@jwt_required()
def trigger_export_csv():

    from celery_app import generate_csv_export
    if request.method == 'OPTIONS':
        return '', 200

    user_id = get_jwt_identity()
    generate_csv_export.delay(user_id)

    return jsonify({'msg': 'CSV export started! You will receive an email shortly.'}), 202



@app.route('/api/admin/users', methods=['GET', 'OPTIONS'])
@jwt_required()
@admin_required
def admin_list_users():
    if request.method == 'OPTIONS':
        return '', 200
    search = request.args.get('search', '')
    query = User.query
    if search:
        search_pattern = f"%{search.lower()}%"
        query = query.filter(
            (User.email.ilike(search_pattern)) | (User.full_name.ilike(search_pattern))
        )
    users = query.order_by(User.id).all()
    return jsonify([
        {
            'id': u.id,
            'email': u.email,
            'full_name': u.full_name,
            'role': u.role,
            'active': u.active
        }
        for u in users
    ]), 200

@app.route('/api/admin/users/<int:user_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@jwt_required()
@admin_required
def admin_edit_delete_user(user_id):
    if request.method == 'OPTIONS':
        return '', 200
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404

    if request.method == 'PUT':
        data = request.get_json()
       
        if 'active' in data:
            user.active = data['active']
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'role' in data:
            user.role = data['role']
        db.session.commit()
        return jsonify({'msg': 'User updated'}), 200

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'msg': 'User deleted'}), 200



@app.route('/api/admin/user_stats/<int:user_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
@admin_required
def admin_user_stats(user_id):
    if request.method == 'OPTIONS':
        return '', 200
    scores = Score.query.filter_by(user_id=user_id).all()
    quiz_stats = []
    for s in scores:
        quiz = Quiz.query.get(s.quiz_id)
        quiz_stats.append({
            'quiz_id': s.quiz_id,
            'quiz_name': quiz.remarks if quiz and quiz.remarks else f"Quiz #{s.quiz_id}",
            'score': round(s.total_scored, 2)
        })
    return jsonify(quiz_stats), 200



from sqlalchemy import func

@app.route('/api/admin/summary_stats', methods=['GET', 'OPTIONS'])
@jwt_required()
@admin_required
def admin_summary_stats():
    if request.method == 'OPTIONS':
        return '', 200

    
    total_users = User.query.count()
    reg_chart = [{'date': f'User {i+1}', 'count': 1} for i in range(total_users)]

    
    quiz_attempts = db.session.query(
        func.strftime('%Y-%W', Score.timestamp),
        func.count(Score.id)
    ).group_by(func.strftime('%Y-%W', Score.timestamp)).order_by(func.min(Score.timestamp)).limit(8).all()
    quiz_chart = [{'date': (x[0] or "N/A"), 'count': x[1]} for x in quiz_attempts]

    
    top_scorers = db.session.query(
        User.full_name, User.email, func.avg(Score.total_scored).label('avg_score')
    ).join(Score, User.id == Score.user_id)\
    .group_by(User.id)\
    .order_by(func.avg(Score.total_scored).desc())\
    .limit(5).all()
    top_scorer_chart = [{
        'full_name': t[0],
        'email': t[1],
        'avg_score': round(t[2], 2)
    } for t in top_scorers]

    return jsonify({
        'userRegistrations': reg_chart,
        'quizAttempts': quiz_chart,
        'topScorers': top_scorer_chart
    }), 200
@app.route('/api/admin/search', methods=['GET', 'OPTIONS'])
@jwt_required()
@admin_required
def admin_global_search():
    if request.method == 'OPTIONS':
        return '', 200
    query = request.args.get('q', '').strip()
    results = {'users': [], 'subjects': [], 'quizzes': []}
    if not query:
        return jsonify(results)

    
    user_matches = User.query.filter(
        (User.email.ilike(f'%{query}%')) | (User.full_name.ilike(f'%{query}%'))
    ).all()
    results['users'] = [
        {'id': u.id, 'email': u.email, 'full_name': u.full_name, 'role': u.role, 'active': u.active}
        for u in user_matches
    ]

   
    subject_matches = Subject.query.filter(
        (Subject.name.ilike(f'%{query}%')) | (Subject.description.ilike(f'%{query}%'))
    ).all()
    results['subjects'] = [
        {'id': s.id, 'name': s.name, 'description': s.description}
        for s in subject_matches
    ]

    
    quiz_matches = Quiz.query.filter(
        Quiz.remarks.ilike(f'%{query}%')
    ).all()
    results['quizzes'] = [
        {'id': q.id, 'remarks': q.remarks, 'chapter_id': q.chapter_id, 'date_of_quiz': q.date_of_quiz.isoformat() if q.date_of_quiz else ""}
        for q in quiz_matches
    ]

    return jsonify(results)




if __name__ == '__main__':
    setup_db()
    app.run(debug=True)
