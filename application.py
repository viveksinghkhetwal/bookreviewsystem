import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://xcnprtumpcosiv:f433bdce0fdf582124511d6cb362aee4b0cb992e464c450e3a0149db02b12f79@ec2-52-0-155-79.compute-1.amazonaws.com:5432/dah2hrgpictefi")
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
            return render_template("error.html",message="Please, enter a valid email id and password. Kindly register if you are not registered.")
        if db.execute("SELECT * FROM userinfo WHERE email=:email AND pwd=:pwd",{"email":email,"pwd":pwd}).rowcount==1:
            email = db.execute("SELECT email from userinfo where email=:email",{"email":email}).fetchone()
            session["id"]=email
            #use email as a variable for userid.
            return redirect(url_for('search'))
    return render_template('login.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    s = request.form.get("search")
    if request.method == 'POST':
        result = db.execute("SELECT * FROM books WHERE title like '%"+s+"%' or isbn like '%"+s+"%' or author like '%"+s+"%' ORDER BY title").fetchall()
        db.commit()
        return render_template("search.html", result=result)
    return render_template("account.html")


@app.route('/search/book/<string:isbn>/<string:title>',methods=['GET','POST'])
def book(title,isbn):
    #Details of the a single book.
    review = request.form.get("review")
    check = db.execute("SELECT * from books where isbn=:id", {"id":isbn}).fetchone()
    for i in session["id"]:
        uid=i
    if request.method=='POST':
        if db.execute("SELECT * from reviews WHERE userid=:ui and bookid=:bi",{"ui":uid,"bi":check.isbn}).rowcount==0:
            try:
                db.execute("INSERT INTO reviews(reviews,userid,bookid) VALUES(:rv,:ui,:bi)",{"rv":review, "ui":uid, "bi":check.isbn})
                db.commit()
                return render_template("bookdetail.html")
            except IntegrityError:
                return render_template("error.html",message="You have submitted your review. User can review only once.")
        if db.execute("SELECT * from reviews WHERE userid=:ui and bookid=:bi",{"ui":uid,"bi":check.isbn}).rowcount==1:
            return render_template("error.html",message="User can review once.")
    if check is None:
        return render_template("error.html", message="No such book exists.")
    userreviews = db.execute("SELECT * from reviews where bookid=:id", {"id":check.isbn}).fetchall()    #get book detail.
    return render_template("bookdetail.html", check=check, userreviews=userreviews,title=title, isbn=isbn)
    engine.dispose()

