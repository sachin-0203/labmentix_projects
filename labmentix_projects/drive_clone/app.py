
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from flask_sqlalchemy import SQLAlchemy
import os, uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET','devsecret')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__),'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drive_clone.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300))
    stored_name = db.Column(db.String(300))

@app.route('/')
def index():
    files = File.query.all()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part'); return redirect(url_for('index'))
    f = request.files['file']
    if f.filename=='': flash('No selected file'); return redirect(url_for('index'))
    fname = secure_filename(f.filename)
    uid = str(uuid.uuid4())
    stored = uid + "_" + fname
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], stored))
    newf = File(filename=fname, stored_name=stored)
    db.session.add(newf); db.session.commit()
    flash('Uploaded')
    return redirect(url_for('index'))

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<int:file_id>')
def delete(file_id):
    f = File.query.get_or_404(file_id)
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f.stored_name))
    except Exception as e:
        pass
    db.session.delete(f); db.session.commit()
    flash('Deleted')
    return redirect(url_for('index'))

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)
