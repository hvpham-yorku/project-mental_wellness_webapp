from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    happiness = db.Column(db.Float, nullable=False)
    anxiety = db.Column(db.Float, nullable=False)
    energy = db.Column(db.Float, nullable=False)
    stress = db.Column(db.Float, nullable=False)
    activity = db.Column(db.String(100))
    notes = db.Column(db.String(500))