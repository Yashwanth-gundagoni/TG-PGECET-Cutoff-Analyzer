from database import db


class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)

    college = db.Column(db.String(250), nullable=False)

    branch = db.Column(db.String(150), nullable=False)

    sno = db.Column(db.Integer)

    percentile = db.Column(db.Float)

    rank = db.Column(db.Integer)

    name = db.Column(db.String(200))

    category = db.Column(db.String(100))

    gender = db.Column(db.String(10))

    region = db.Column(db.String(50))

    allotted_category = db.Column(db.String(100))

    phase = db.Column(db.String(30))

    year = db.Column(db.Integer)