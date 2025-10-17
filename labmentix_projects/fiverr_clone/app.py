
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET','devsecret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fiverr_clone.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(20), default='buyer')  # buyer or seller

class Gig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route('/')
def index():
    gigs = Gig.query.all()
    return render_template('index.html', gigs=gigs)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role','buyer')
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        user = User(name=name, email=email, password_hash=generate_password_hash(password), role=role)
        db.session.add(user); db.session.commit()
        flash('Registered successfully. Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['role'] = user.role
            flash('Logged in')
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/create_gig', methods=['GET','POST'])
def create_gig():
    if 'user_id' not in session or session.get('role')!='seller':
        flash('Only sellers can create gigs. Please login as seller.')
        return redirect(url_for('login'))
    if request.method=='POST':
        title = request.form['title']; desc = request.form['description']; price = float(request.form['price'])
        gig = Gig(title=title, description=desc, price=price, seller_id=session['user_id'])
        db.session.add(gig); db.session.commit()
        flash('Gig created')
        return redirect(url_for('index'))
    return render_template('create_gig.html')

@app.route('/gig/<int:gig_id>')
def gig_detail(gig_id):
    gig = Gig.query.get_or_404(gig_id)
    seller = User.query.get(gig.seller_id)
    return render_template('gig_detail.html', gig=gig, seller=seller)

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
