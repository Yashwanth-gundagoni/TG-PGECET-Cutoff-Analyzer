from flask import Blueprint, render_template

cutoff_range_bp = Blueprint(
    "cutoff_range",
    __name__
)


@cutoff_range_bp.route("/cutoff-range")
def cutoff_range():
    return render_template("cutoff_range.html")