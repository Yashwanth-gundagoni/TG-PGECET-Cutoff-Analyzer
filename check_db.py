from app import app
from models import Candidate

with app.app_context():
    total = Candidate.query.count()

    print(f"Total Candidates in Database: {total}")

    candidates = Candidate.query.limit(5).all()

    print("\nFirst 5 Records:\n")

    for candidate in candidates:
        print(
            candidate.id,
            candidate.college,
            candidate.rank,
            candidate.name
        )