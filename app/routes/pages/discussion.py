from flask import render_template, Blueprint, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import db, Discussion, User

discussion_bp = Blueprint('discussion', __name__)

@discussion_bp.route('/discussion/<int:discussion_id>')
def discussion(discussion_id):
    ds = Discussion.query.get_or_404(discussion_id)
    user = User.query.get(ds.user_id)
    return render_template("pages/discussion.html", ds={
        "title": ds.title,
        "content": ds.content,
        "time_created": ds.time_created,
        'user': {
            'name': user.username if user else "Unknown",
            'avatar': user.avatar if user else None
            }
    })
