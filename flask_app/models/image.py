from flask_app.models.db import db


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    user = db.Column(db.Integer, nullable=False)
    profile = db.Column(db.Text, nullable=False)
