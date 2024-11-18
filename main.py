from flask import Flask, redirect, url_for
from source_websites.source_website_routes import source_website_bp
from documents.documents_routes import documents_bp
from requirements.requirements_routes import requirements_bp

app = Flask(__name__)

# Register the blueprint for source website routes
app.register_blueprint(source_website_bp, url_prefix='/source_websites')

# Register the blueprint for document routes
app.register_blueprint(documents_bp, url_prefix='/documents')

app.register_blueprint(requirements_bp, url_prefix='/requirements')

# Add a root route that redirects to the documents page
@app.route('/')
def index():
    return redirect(url_for('documents.index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)