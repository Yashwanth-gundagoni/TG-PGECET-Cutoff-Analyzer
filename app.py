from flask import Flask, render_template

from database import db
from models import Candidate


app = Flask(__name__)

@app.context_processor
def inject_request_path():
    from flask import request
    return dict(current_path=request.path)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pgecet.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)