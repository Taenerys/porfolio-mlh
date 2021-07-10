from datetime import datetime
from logging import NullHandler
from db import db

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    like_count = db.Column(db.Integer, default=0)
    img = db.Column(db.Text, nullable=False)
    img_name = db.Column(db.Text, nullable=False)
    img_mimetype = db.Column(db.Text, nullable=False)
