from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from model import db, User, MoodLog
from forms import RegistrationForm, LoginForm, MoodLogForm
from config import Config
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import google.generativeai as genai

#Gemini Key
genai.configure(api_key="your key")


def generate_response(prompt):
    model = genai.GenerativeModel("models/gemini-1.5-pro")
    response = model.generate_content([prompt])
    return response.text


# Flask app
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
analyzer = SentimentIntensityAnalyzer()

# login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Route Patient View
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid login.')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html', user=current_user)


@app.route('/logmood', methods=['GET', 'POST'])
@login_required
def log_mood():
    form = MoodLogForm()
    support_msg = None

    if form.validate_on_submit():
        sentiment_scores = analyzer.polarity_scores(form.text_entry.data)
        compound_score = sentiment_scores['compound']
        sentiment = (
            "positive" if compound_score >= 0.05 else
            "negative" if compound_score <= -0.05 else "neutral"
        )

        mood = MoodLog(
            user_id=current_user.id,
            text_entry=form.text_entry.data,
            mood_score=form.mood_score.data
        )
        db.session.add(mood)
        db.session.commit()

        prompt = f'The user just wrote: "{form.text_entry.data}". Respond with one short, supportive sentence like a kind mental health coach.'
        support_msg = generate_response(prompt)

        return render_template('logmood.html', form=form, support_msg=support_msg, sentiment=sentiment)

    return render_template('logmood.html', form=form)


# Doctor view

@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash("Unauthorized.")
        return redirect(url_for('home'))

    patients = User.query.filter_by(role='patient').all()
    return render_template('doctordash.html', patients=patients)


@app.route('/doctor/patient/<int:user_id>')
@login_required
def view_patient(user_id):
    if current_user.role != 'doctor':
        flash("Unauthorized.")
        return redirect(url_for('home'))

    patient = User.query.get_or_404(user_id)
    mood_logs = MoodLog.query.filter_by(user_id=user_id).order_by(MoodLog.timestamp.asc()).all()

    # mood plot
    import matplotlib.pyplot as plt
    import io, base64

    dates = [log.timestamp.strftime("%Y-%m-%d") for log in mood_logs]
    scores = [log.mood_score for log in mood_logs]

    plt.figure()
    plt.plot(dates, scores, marker='o')
    plt.title(f"Mood Trend for {patient.email}")
    plt.xlabel("Date")
    plt.ylabel("Mood Score")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded = base64.b64encode(buf.getvalue()).decode()
    buf.close()

    # AI summary
    if mood_logs:
        text_snippets = [log.text_entry for log in mood_logs[-7:]]  
        combined_text = "\n".join(text_snippets)

        prompt = (
            f"As a mental health assistant, please summarize the patient's overall mood trend based on the following journal entries.\n\n"
            f"{combined_text}\n\n"
            f"Please answer with:\n"
            f"1. Emotional Summary (2-3 sentences)\n"
            f"2. Top 3 keywords\n"
            f"3. Suggested action if needed."
        )
        ai_summary = generate_response(prompt)
    else:
        ai_summary = "No mood entries available yet."

    return render_template('patientchart.html', patient=patient, chart_data=encoded, ai_summary=ai_summary)

# Run
if __name__ == "__main__":
    app.run(debug=True)
