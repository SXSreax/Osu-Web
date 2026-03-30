from flask import render_template, Blueprint, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app.models import db, Discussion, User, Comment, Favorite_Discussion
from app.forms import CommentForm
from datetime import datetime

discussion_bp = Blueprint('discussion', __name__)

@discussion_bp.route('/discussion/<int:discussion_id>', methods=['GET', 'POST'])
def discussion(discussion_id):
    ds = Discussion.query.get_or_404(discussion_id)
    user = User.query.get(ds.user_id)
    
    form = CommentForm()
    
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You must be logged in to comment.", "danger")
            return redirect(url_for("discussion.discussion", discussion_id=discussion_id))
        
        new_comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            discussion_id=discussion_id
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added!", "success")
        return redirect(url_for("discussion.discussion", discussion_id=discussion_id))

    comments = Comment.query.filter_by(discussion_id=discussion_id).order_by(Comment.time_created.asc()).all()
    
    ds_data = {
        "id": ds.id,
        "title": ds.title,
        "content": ds.content,
        "time_created": ds.time_created,
        'user': {
            'name': user.username if user else "Unknown",
            'avatar': user.avatar if user else None
        }
    }

    favorited = False
    if current_user.is_authenticated:
        favorited = Favorite_Discussion.query.filter_by(
            user_id=current_user.id,
            discussion_id=ds.id
        ).first() is not None
    
    return render_template("pages/discussion.html", ds=ds_data, comments=comments, form=form, favorited=favorited)

@discussion_bp.route('/discussion/<int:discussion_id>/favorite', methods=['POST'])
def favorite(discussion_id):
    existing = Favorite_Discussion.query.filter_by(user_id=current_user.id, discussion_id=discussion_id).first()

    if existing:
        db.session.delete(existing)
        status = "removed"
    else:
        db.session.add(Favorite_Discussion(user_id=current_user.id, discussion_id=discussion_id))
        status = "added"

    db.session.commit()
    return jsonify({"status": status})
