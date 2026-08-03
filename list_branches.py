from app import app
from database import db
from models import Candidate


with app.app_context():

    branches = (
        db.session.query(Candidate.branch)
        .distinct()
        .order_by(Candidate.branch)
        .all()
    )

    print(f"Total Distinct Branches: {len(branches)}")
    print("-" * 60)

    for i, (branch,) in enumerate(branches, start=1):
        print(f"{i:2}. {branch}")
        