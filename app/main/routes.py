from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.main import bp
from app.models import Document

@bp.route('/')
def index():
    """Home page route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html', title='Home')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route for authenticated users."""
    # Get recent documents for the current user
    recent_documents = Document.get_by_user(current_user.id, limit=5)
    
    # Get total document count
    all_documents = Document.get_by_user(current_user.id)
    total_documents = len(all_documents)
    
    return render_template('main/dashboard.html', 
                         title='Dashboard',
                         recent_documents=recent_documents,
                         total_documents=total_documents)

@bp.route('/evidence-repository')
@login_required
def evidence_repository():
    """Evidence repository route to display all documents."""
    documents = Document.get_by_user(current_user.id)
    return render_template('main/evidence_repository.html', 
                         title='Evidence Repository',
                         documents=documents)