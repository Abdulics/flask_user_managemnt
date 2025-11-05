from flask import render_template, Blueprint

bp = Blueprint('landing_page', __name__)

@bp.route('/')
def landing_page():
    return render_template('index.html')