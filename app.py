from flask import Flask, render_template

from database import db
from models import Candidate
from sqlalchemy import distinct
from routes.cutoff_range import cutoff_range_bp

app = Flask(__name__)

@app.context_processor
def inject_request_path():
    from flask import request
    return dict(current_path=request.path)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pgecet.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.register_blueprint(cutoff_range_bp)


@app.route("/api/branches")
def get_branches():

    branches = (
        db.session.query(Candidate.branch)
        .distinct()
        .order_by(Candidate.branch)
        .all()
    )

    database_branches = [branch[0] for branch in branches]

    result = {}

    for stream, mapped_branches in BRANCH_MAPPING.items():

        stream_branches = []

        for branch in mapped_branches:

            if branch in database_branches:
                stream_branches.append(branch)

        if stream_branches:
            result[stream] = sorted(stream_branches)

    return result


@app.route("/api/colleges")
def get_colleges():

    colleges = (
        db.session.query(Candidate.college)
        .distinct()
        .order_by(Candidate.college)
        .all()
    )

    return {
        "colleges": [college[0] for college in colleges]
    }

@app.route("/api/colleges-by-branches")
def get_colleges_by_branches():

    from flask import request

    branches = request.args.getlist("branch")

    if not branches:
        return {"colleges": []}

    colleges = (
        db.session.query(Candidate.college)
        .filter(Candidate.branch.in_(branches))
        .distinct()
        .order_by(Candidate.college)
        .all()
    )

    return {
        "colleges": [college[0] for college in colleges]
    }

@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)