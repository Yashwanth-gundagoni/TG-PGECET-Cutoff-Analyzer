from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pgecet.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    college = db.Column(db.String(200), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    phase = db.Column(db.String(50), nullable=False)
    rank = db.Column(db.Integer, nullable=False)


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)