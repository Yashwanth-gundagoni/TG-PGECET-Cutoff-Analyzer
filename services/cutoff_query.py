from sqlalchemy import func

from database import db
from models import Candidate


def build_cutoff_query(
    year,
    category,
    branches,
    colleges,
    gender
):
    """
    Returns a SQLAlchemy query that contains
    one row per closing cutoff.
    """

    query = db.session.query(
        Candidate.year.label("year"),
        Candidate.college.label("college"),
        Candidate.branch.label("branch"),
        Candidate.category.label("category"),
        Candidate.gender.label("gender"),
        func.max(Candidate.rank).label("closing_rank")
    )

    # ------------------------
    # Apply Filters
    # ------------------------

    if year:
        query = query.filter(
            Candidate.year == int(year)
        )

    if category:
        query = query.filter(
            Candidate.category == category
        )

    if branches:
        query = query.filter(
            Candidate.branch.in_(branches)
        )

    if colleges:
        query = query.filter(
            Candidate.college.in_(colleges)
        )

    if gender:
        query = query.filter(
            Candidate.gender == gender
        )

    # ------------------------
    # GROUP BY
    # ------------------------

    if gender:

        query = query.group_by(
            Candidate.year,
            Candidate.college,
            Candidate.branch,
            Candidate.category
        )

    else:

        query = query.group_by(
            Candidate.year,
            Candidate.college,
            Candidate.branch,
            Candidate.category,
            Candidate.gender
        )

    return query