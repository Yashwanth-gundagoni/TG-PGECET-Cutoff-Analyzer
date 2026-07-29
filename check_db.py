from app import app
from models import Candidate
from database import db

with app.app_context():

    print("=" * 50)
    print("TG PGECET DATABASE SUMMARY")
    print("=" * 50)

    # Total candidates
    total_candidates = Candidate.query.count()
    print(f"\nTotal Candidates : {total_candidates}")

    # Year-wise candidate count
    print("\nCandidates by Year")
    print("-" * 25)

    years = (
        db.session.query(Candidate.year)
        .distinct()
        .order_by(Candidate.year)
        .all()
    )

    for (year,) in years:
        count = Candidate.query.filter_by(year=year).count()
        print(f"{year} : {count}")

    # Year-wise unique colleges
    print("\nUnique Colleges by Year")
    print("-" * 25)

    for (year,) in years:
        colleges = (
            db.session.query(Candidate.college)
            .filter(Candidate.year == year)
            .distinct()
            .count()
        )

        print(f"{year} : {colleges}")

    # First 5 records
    print("\nFirst 5 Records")
    print("-" * 25)

    candidates = Candidate.query.limit(5).all()

    for candidate in candidates:
        print(
            candidate.id,
            candidate.year,
            candidate.college,
            candidate.rank,
            candidate.name
        )

    print("\n" + "=" * 50)