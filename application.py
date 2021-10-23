import os
import requests

from flask import Flask, flash, session, render_template, request, redirect, url_for
from flask_session import Session
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError, OperationalError

app = Flask(__name__)


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Set up database
engine = create_engine("postgresql://xcnprtumpcosiv:f433bdce0fdf582124511d6cb362aee4b0cb992e464c450e3a0149db02b12f79@ec2-52-0-155-79.compute-1.amazonaws.com:5432/dah2hrgpictefi", pool_size = 20, max_overflow=10)
db = scoped_session(sessionmaker(bind=engine))


# For pagination with starting letters of the Book's Title.
letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

@app.route("/")
@app.route("/home")
def index():
    session.clear()
    return render_template("home.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        fname = request.form.get("fname")
        email = request.form.get("email")
        newpwd = request.form.get("newpwd")
        confpwd = request.form.get("confpwd")
        if request.method == 'POST':
            if newpwd == confpwd:
                try:
                    db.execute("INSERT INTO userinfo(fname, email, pwd) VALUES(:fname, :email, :pwd)",{"fname":fname, "email":email, "pwd":newpwd})
                    db.commit()
                except IntegrityError:
                    flash('This email is already registered with us. Please, try to Login! or use a different email address for Signup!', 'danger')
                    return render_template('signup.html')
                    # return render_template("error2.html",heading="Signup Error", message="This email is already registered with us. Please, try to Login! or use a different email address for Signup!")
                # do stuff when the form is submitted

                # redirect to end the POST handling
                # the redirect can be to the same route or somewhere else
                flash('You are successfully registered.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Your password does not match.', 'danger')

        # show the form, it wasn't submitted
        return render_template('signup.html')
    except OperationalError:
        return render_template("offline.html",heading= "No Internet", message="You are Offline. Please connect with internet and try registering again.")

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        email = request.form.get("username")
        pwd = request.form.get("pswd")
        if request.method == 'POST':
            if db.execute("SELECT * FROM userinfo WHERE email=:email AND pwd=:pwd",{"email":email,"pwd":pwd}).rowcount==0:
                flash("Please enter a valid email id and password. Kindly register if you are not registered.", "danger")
                return render_template('login.html')
                # return render_template("error2.html",heading="Error", message="Please, enter a valid email id and password. Kindly register if you are not registered.")
            if db.execute("SELECT * FROM userinfo WHERE email=:email AND pwd=:pwd",{"email":email,"pwd":pwd}).rowcount==1:
                fname = db.execute("SELECT fname from userinfo where email=:email",{"email":email}).fetchone()
                session["id"]=fname
                #use email as a variable for userid.
                return redirect(url_for('search'))
        return render_template('login.html')
    except OperationalError:
        return render_template("offline.html",heading= "No Internet", message="You are Offline. Please connect with internet and try login again.")



@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        s = str(request.form.get("search")).lower()
        if request.method == 'POST':
            # Dynamic search bar.
            result = db.execute("SELECT books.*, newisbn.isbn13 FROM books INNER JOIN newisbn on books.isbn=newisbn.isbn WHERE LOWER(books.title) LIKE '%"+s+"%' or books.isbn like '%"+s+"%' or LOWER(books.author) like '%"+s+"%' ORDER BY title").fetchall()
        else:
            # INNER JOIN tables books and newisbn.
            result = db.execute("SELECT books.*, newisbn.isbn13 FROM books INNER JOIN newisbn on books.isbn=newisbn.isbn ORDER BY id LIMIT 52").fetchall()
        return render_template("search.html", result = result, letters=letters, count=len(result))
    except OperationalError:
        return render_template("offline.html",heading= "No Internet", message="You are Offline. Please connect with internet and try again.")



@app.route('/search/<string:alpha>', methods=['GET','POST'])
def searchbook(alpha):
    try:
        s = str(request.form.get("search")).lower()
        if request.method == 'POST':
            # Dynamic search bar.
            result = db.execute("SELECT books.*, newisbn.isbn13 FROM books INNER JOIN newisbn on books.isbn=newisbn.isbn WHERE LOWER(books.title) LIKE '%"+s+"%' or books.isbn like '%"+s+"%' or LOWER(books.author) like '%"+s+"%' ORDER BY title").fetchall()
        else:
            result = db.execute("SELECT books.*, newisbn.isbn13 FROM books INNER JOIN newisbn on books.isbn=newisbn.isbn WHERE books.title LIKE '"+alpha+"%' ORDER BY title").fetchall()
        return render_template("search.html", result = result, letters=letters, count=len(result))
    except OperationalError:
        return render_template("offline.html",heading= "No Internet", message="You are Offline. Please connect with internet and try login again.")



@app.route('/search/book/<string:isbn>/<string:title>',methods=['GET','POST'])
def book(title,isbn):
    #Details of the a single book.
    try:
        review = request.form.get("review")
        check = db.execute("SELECT * from books where isbn=:id", {"id":isbn}).fetchone()

        author_name = check.author.replace(" ", "_")
        author_bio = requests.get(f"https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles={author_name}")
        author_data = author_bio.json()["query"]["pages"]
        for key in author_data:
            authorid = key
        author_data = author_data[authorid]["extract"]

        book_bio = requests.get(f"https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles={check.title}")
        book_data = book_bio.json()["query"]["pages"]
        for key in book_data:
            bookid = key
        if bookid == "-1":
            book_data = 0
        else:
            book_data = book_data[bookid]["extract"]

        # Using GoodReads API to store all details of the book
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"isbns":check.isbn})
        details = res.json()["books"][0]

        desc = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}")
        if desc.json()["totalItems"] == 0:
            content = 0
        else:
            content = desc.json()["items"][0]["volumeInfo"]

        # getimg = requests.get("https://covers.openlibrary.org/b/:key/:value-:size.jpg", params={"key":"isbn", "value":details["isbn13"], "size":"S"})

        userreviews = db.execute("SELECT * from reviews where isbn_no=:id", {"id":check.isbn}).fetchall()    #get book detail.
        
        for i in session["id"]:
            uid=i

        if request.method=='POST':
            time = datetime.now()
            if db.execute("SELECT * from reviews WHERE username=:ui and isbn_no=:bi and reviews=:review",{"ui":uid,"bi":check.isbn, "review":review}).rowcount==0:
                try:
                    db.execute("INSERT INTO reviews(reviews, username, isbn_no, time) VALUES(:rv,:ui,:bi, :dt)",{"rv":review, "ui":uid, "bi":check.isbn, "dt":time})
                    db.commit()
                    return book(title, isbn)
                except IntegrityError:
                    return render_template("error.html",heading= "Error", message="You have submitted your review. User can review only once.")
            # else:
            #     return render_template("error.html",message="You have submitted your review. User can review once.")
        if check is None:
            return render_template("error.html", heading = "Search Error", message="No such book exists.")
        return render_template("bookdetail.html", check=check, userreviews=userreviews,title=title, isbn=isbn, details=details, content=content, authordata = author_data, bookdata = book_data)
        engine.dispose()
    except KeyError:
        return render_template("error2.html",heading="Login Error", message="Please, Login to continue!")
    # except OperationalError:
    #     return render_template("offline.html",heading= "Offline", message="You are Offline. Please connect with internet and try again.")

    
if __name__ == '__main__':
   app.run(debug=True)        
