from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arg_game.db'
db = SQLAlchemy(app)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    current_chapter = db.Column(db.Integer, nullable=False, default=0)
    hints_used = db.Column(db.Integer, nullable=False, default=0)

class Story:
    title = "Mystery Adventure"
    content = [
        "Welcome to the adventure! Your first task is to go to the old library and find the hidden book.",
        "Great job! Now, head to the town square and look for the statue with a plaque."
    ]
    questions = [
        {"question": "What is the name of the book you found?", "answer": "The Hidden Treasure"},
        {"question": "What is written on the statue's plaque?", "answer": "In Memory of the Brave"}
    ]
    hints = [
        "The book is in the history section.",
        "The plaque is located at the base of the statue."
    ]

story = Story()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start/<user_id>')
def start(user_id):
    if not UserProgress.query.filter_by(user_id=user_id).first():
        new_user = UserProgress(user_id=user_id)
        db.session.add(new_user)
        db.session.commit()
    return redirect(url_for('game', user_id=user_id))

@app.route('/game/<user_id>', methods=['GET', 'POST'])
def game(user_id):
    user_progress = UserProgress.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        answer = request.form['answer']
        if answer.lower() == story.questions[user_progress.current_chapter]['answer'].lower():
            user_progress.current_chapter += 1
            db.session.commit()
            if user_progress.current_chapter >= len(story.content):
                return render_template('congratulations.html')
        else:
            return render_template('game.html', content=story.content[user_progress.current_chapter], question=story.questions[user_progress.current_chapter]['question'], error=True)
    
    return render_template('game.html', content=story.content[user_progress.current_chapter], question=story.questions[user_progress.current_chapter]['question'], error=False)

@app.route('/hint/<user_id>')
def hint(user_id):
    user_progress = UserProgress.query.filter_by(user_id=user_id).first()
    hint = story.hints[user_progress.current_chapter]
    user_progress.hints_used += 1
    db.session.commit()
    return render_template('hint.html', hint=hint)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
