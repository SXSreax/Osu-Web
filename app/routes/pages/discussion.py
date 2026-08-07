from flask import render_template, Blueprint, redirect, url_for, flash, jsonify
from sqlalchemy import update
from flask_login import current_user
from app.models import db, Discussion, User, Comment, Favorite_Discussion
from app.forms import CommentForm

discussion_bp = Blueprint('discussion', __name__)


@discussion_bp.route('/discussion/<int:discussion_id>',
                     methods=['GET', 'POST'])
def discussion(discussion_id):
    """
    Display a discussion thread and handle new comments.

    Inputs:
        - GET: discussion ID from the route
        - POST: comment content from the form

    Processing:
        - Load the discussion and its author.
        - Validate and save a new comment when submitted.
        - Prepare the discussion and comment data for rendering.

    Outputs:
        - Renders the discussion page with comments and form state.
        - Redirects back to the discussion after a successful comment
            submission.
    """
    ds = Discussion.query.get_or_404(discussion_id)
    user = User.query.get(ds.user_id)

    form = CommentForm()

    if form.validate_on_submit():
        # Collect the submitted comment and save it to the discussion.
        if not current_user.is_authenticated:
            # Require a login before creating a comment to avoid
            # anonymous posting.
            flash("You must be logged in to comment.", "danger")
            return redirect(url_for("discussion.discussion",
                                    discussion_id=discussion_id))

        new_comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            discussion_id=discussion_id
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added!", "success")
        return redirect(url_for("discussion.discussion",
                                discussion_id=discussion_id))

    # Gather all comments in chronological order for display.
    comments = Comment.query.filter_by(
        discussion_id=discussion_id).order_by(Comment.time_created.asc()).all()

    ds_data = {
        "id": ds.id,
        "title": ds.title,
        "content": ds.content,
        "time_created": ds.time_created,
        "like": ds.like,
        'user': {
            'name': user.username if user else "Unknown",
            'avatar': user.avatar if user else None
        }
    }

    # Check whether the current user has already favorited this discussion.
    favorited = False
    if current_user.is_authenticated:
        favorited = Favorite_Discussion.query.filter_by(
            user_id=current_user.id,
            discussion_id=ds.id
        ).first() is not None

    return render_template("pages/discussion.html",
                           ds=ds_data,
                           comments=comments,
                           form=form,
                           favorited=favorited)


@discussion_bp.route('/discussion/<int:discussion_id>/favorite',
                     methods=['POST'])
def favorite(discussion_id):
    """
    Toggle the favorite status for a discussion.

    Inputs:
        - POST: discussion ID from the route

    Processing:
        - Check whether the current user already favorited the discussion.
        - Add or remove the favorite record and adjust the discussion
            like count.

    Outputs:
        - Returns JSON indicating whether the discussion was added or removed.
    """
    existing = Favorite_Discussion.query.filter_by(
        user_id=current_user.id,
        discussion_id=discussion_id).first()

    if existing:
        # Remove the favorite entry when the user already liked it
        # to toggle it off.
        db.session.delete(existing)
        status = "removed"
        db.session.execute(
            update(Discussion)
            .where(Discussion.id == discussion_id)
            .values(like=Discussion.like - 1)
        )
    else:
        db.session.add(Favorite_Discussion(
            user_id=current_user.id,
            discussion_id=discussion_id))
        status = "added"
        db.session.execute(
            update(Discussion)
            .where(Discussion.id == discussion_id)
            .values(like=Discussion.like + 1)
        )

    db.session.commit()
    return jsonify({"status": status})
