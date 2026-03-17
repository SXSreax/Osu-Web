from flask import render_template, Blueprint, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import db, Discussion, User
from app.forms import DiscussionForm

community_bp = Blueprint('community', __name__)

@community_bp.route('/community/')
def community():
    discussion = Discussion.query.order_by(Discussion.time_created.desc()).all()
    discussions = []
    for ds in discussion:
        user = User.query.get(ds.user_id)

        discussions.append({
            'id': ds.id,
            'title': ds.title,
            'content': ds.content,
            'user': {
                'name': user.username if user else "Unknown",
                'avatar': user.avatar if user else None
            }
        })

    return render_template('pages/community.html', discussions=discussions)

@community_bp.route('/community/create_discussion/', methods=["GET", "POST"])
@login_required
def create_discussion():
    form = DiscussionForm()
    if form.validate_on_submit():
        title = form.data.get("title")
        content = form.data.get("content")

        discussion = Discussion(
            title=title,
            content=content,
            user_id=current_user.id
        )

        db.session.add(discussion)
        db.session.commit()
        flash("Created discussion", "success")
        return redirect(url_for('community.community'))

    return render_template('pages/create_discussion.html', form=form)