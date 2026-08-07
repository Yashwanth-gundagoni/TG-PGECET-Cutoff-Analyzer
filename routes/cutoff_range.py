from flask import Blueprint, render_template, request

from sqlalchemy import func

from database import db

from models import Candidate

from mappings.branch_streams import BRANCH_MAPPING

from services.cutoff_query import build_cutoff_query


cutoff_range_bp = Blueprint(
    "cutoff_range",
    __name__
)


@cutoff_range_bp.route("/cutoff-range")
def cutoff_range():

    year = request.args.get("year")
    category = request.args.get("category")

    streams = request.args.getlist("streams")
    branches = request.args.getlist("branches")
    colleges = request.args.getlist("colleges")

    gender = request.args.get("gender")

    min_rank = request.args.get("min_rank", type=int)
    max_rank = request.args.get("max_rank", type=int)
    max_available_rank = db.session.query(
        func.max(Candidate.rank)
    ).scalar()

    return render_template(

        "cutoff_range.html",

        year=year,
        category=category,

        streams=streams,
        branches=branches,
        colleges=colleges,

        gender=gender,

        min_rank=min_rank,
        max_rank=max_rank,
        max_available_rank=max_available_rank


    )

@cutoff_range_bp.route("/cutoff-range/results")
def cutoff_results():
    # -----------------------
    # Read Filters
    # -----------------------

    
    year = request.args.get("year")
    category = request.args.get("category")

    streams = request.args.getlist("streams")
    branches = request.args.getlist("branches")
    colleges = request.args.getlist("colleges")

    gender = request.args.get("gender")

    # ---------------------------------
    # Expand streams into branches
    # ---------------------------------

    if streams and not branches:

        expanded_branches = []

        for stream in streams:
            expanded_branches.extend(
                BRANCH_MAPPING.get(stream, [])
            )

        branches = list(dict.fromkeys(expanded_branches))
    
        
    
    min_rank = request.args.get("min_rank", type=int)
    max_rank = request.args.get("max_rank", type=int)

    # -----------------------
# Rank Validation
# -----------------------

    if (
        min_rank is not None
        and max_rank is not None
        and min_rank > max_rank
    ):
        max_available_rank = db.session.query(
            func.max(Candidate.rank)
        ).scalar()

        return render_template(

            "cutoff_range.html",

            year=year,
            category=category,

            streams=streams,
            branches=branches,
            colleges=colleges,

            gender=gender,

            min_rank=min_rank,
            max_rank=max_rank,
            max_available_rank=max_available_rank,

            error="From Rank cannot be greater than To Rank."

        )
    
    
    page = request.args.get("page", 1, type=int)
    
    # -----------------------
    # Build Query
    # -----------------------
    
            # -----------------------
        # Build Closing Rank Query
        # -----------------------
    
    query = build_cutoff_query(
        year=year,
        category=category,
        branches=branches,
        colleges=colleges,
        gender=gender
    )
    
        # -----------------------
        # Convert to Subquery
        # -----------------------
    
    cutoff_query = query.subquery()
    
    final_query = db.session.query(
        cutoff_query
    )
    
        # -----------------------
        # Apply Rank Range
        # (Option B)
        # -----------------------
    
    if min_rank is not None:
        final_query = final_query.filter(
            cutoff_query.c.closing_rank >= min_rank
        )
    
    if max_rank is not None:
        final_query = final_query.filter(
            cutoff_query.c.closing_rank <= max_rank
        )
    
        # -----------------------
        # Sort
        # -----------------------
    
    final_query = final_query.order_by(
        cutoff_query.c.closing_rank
    )
    
        # -----------------------
        # Pagination
        # -----------------------
    
    results = final_query.paginate(
        page=page,
        per_page=40,
        error_out=False
    )
    
    return render_template(
        "cutoff_results.html",
        results=results,
        year=year,            
        category=category,
        streams=streams,
        branches=branches,
        colleges=colleges,
        gender=gender,
        min_rank=min_rank,
        max_rank=max_rank
    )