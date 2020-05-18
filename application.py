import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("home.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    fname = request.form.get("fname")
    email = request.form.get("email")
    pwd = request.form.get("pwd")
    if request.method == 'POST':
        try:
            db.execute("INSERT INTO userinfo(fname, email, pwd) VALUES(:fname, :email, :pwd)",{"fname":fname, "email":email, "pwd":pwd})
            db.commit()
        except IntegrityError:
            return render_template("error.html",message="This email is already registered with us. Please, try to Login! or use a different email address for Signup!")
        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('login'))

    # show the form, it wasn't submitted
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get("username")
    pwd = request.form.get("pswd")
    if request.method == 'POST':
        if db.execute("SELECT * FROM userinfo WHERE email=:email AND pwd=:pwd",{"email":email,"pwd":pwd}).rowcount==0:
            return render_template("error.html",message="Please, enter a valid email id and password.")
        if db.execute("SELECT * FROM userinfo WHERE email=:email AND pwd=:pwd",{"email":email,"pwd":pwd}).rowcount==1:
            return redirect(url_for('account'))

    return render_template('login.html')

@app.route('/account', methods=['GET', 'POST'])
def account():
    textr = request.form.get("search")
    if request.method == 'POST':
        result = db.execute("SELECT * FROM books WHERE title like '%"+textr+"%' ORDER BY title").fetchall()
        db.commit()
        return render_template("search.html", result=result)
    return render_template("account.html")
