from flask import render_template, Blueprint, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import db, Discussion, User
from app.forms import DiscussionForm

community_bp = Blueprint('community', __name__)


@community_bp.route('/community/')
def community():
    """
    Render the community discussion page.

    Inputs:
        - GET: None

    Processing:
        - Fetch discussions ordered by creation time.
        - Gather each discussion's author details for display.

    Outputs:
        - Renders the community page with the prepared discussion list.
    """
    # Show the newest discussions first so recent activity is easy to find.
    # Query discussions newest-first so the page shows recent activity first.
    discussion = Discussion.query.order_by(
        Discussion.time_created.desc()).all()
    discussions = []
    # Gather all relevant discussion data for display.
    # Resolve each discussion author for the card shown in the template.
    for ds in discussion:
        user = User.query.get(ds.user_id)

        discussions.append({
            'id': ds.id,
            'title': ds.title,
            'content': ds.content,
            'like': ds.like,
            'user': {
                # Use a fallback when an old discussion has no user.
                'name': user.username if user else "Unknown",
                'avatar': user.avatar if user else None
            }
        })

    return render_template('pages/community.html', discussions=discussions)


@community_bp.route('/community/create_discussion/', methods=["GET", "POST"])
@login_required
def create_discussion():
    """
    Create a new discussion entry.

    Inputs:
        - GET: None
        - POST: discussion title and content from the form

    Processing:
        - On GET: Show the discussion creation form.
        - On POST: Validate the form, create a discussion, and save it.

    Outputs:
        - Renders the creation form (GET)
        - Redirects back to the community page after a successful post.
    """
    form = DiscussionForm()
    # Persist a discussion only after WTForms validation succeeds.
    if form.validate_on_submit():
        # Collect the submitted discussion details.
        title = form.data.get("title")
        content = form.data.get("content")

        discussion = Discussion(
            title=title,
            content=content,
            user_id=current_user.id
        )

        # Stage the new row, then commit it before redirecting to the listing.
        db.session.add(discussion)
        db.session.commit()
        flash("Created discussion", "success")
        # Redirect after saving so the page refreshes with the new discussion.
        return redirect(url_for('community.community'))

    return render_template('pages/create_discussion.html', form=form)
