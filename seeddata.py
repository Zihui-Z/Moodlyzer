import random
from datetime import datetime, timedelta
from app import app, db, User, MoodLog

# sample
mood_entries = [
    ("Feeling optimistic today.", 5),
    ("A bit stressed but okay.", 3),
    ("Very anxious about work.", 2),
    ("Had a great day!", 5),
    ("Feeling low and overwhelmed.", 1),
    ("Pretty calm and collected today.", 4),
    ("Exhausted and worried.", 2),
    ("Joyful after meeting friends.", 5),
    ("Nervous about upcoming exams.", 2),
    ("Peaceful evening at home.", 4),
    ("Feeling grateful for small things.", 5),
    ("Frustrated by slow progress.", 2),
    ("Energetic and hopeful.", 5),
    ("Lonely but trying to stay positive.", 3),
    ("Calm morning, anxious afternoon.", 3),
    ("Overwhelmed with responsibilities.", 1),
    ("Relaxed after meditation.", 5),
    ("Mood swings throughout the day.", 2),
    ("Satisfied with today's work.", 4),
    ("Feeling disconnected.", 2),
]

# sample patient account
def create_patients():
    for i in range(1, 11):
        email = f"patient{i:03}@example.com"
        password = "password123"
        if not User.query.filter_by(email=email).first():
            user = User(email=email, role='patient')
            user.set_password(password)
            db.session.add(user)
    db.session.commit()
    print("✅ Patients created.")

# mood log
def create_mood_logs():
    patients = User.query.filter_by(role='patient').all()
    for patient in patients:
        for _ in range(50):
            text_entry, mood_score = random.choice(mood_entries)
            days_ago = random.randint(0, 49)
            timestamp = datetime.utcnow() - timedelta(days=days_ago)
            mood_log = MoodLog(
                user_id=patient.id,
                text_entry=text_entry,
                mood_score=mood_score,
                timestamp=timestamp
            )
            db.session.add(mood_log)
    db.session.commit()
    print("✅ Mood logs created.")

# main
if __name__ == "__main__":
    with app.app_context():
        create_patients()
        create_mood_logs()