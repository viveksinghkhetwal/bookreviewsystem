import csv
import os, requests, time
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgresql://xcnprtumpcosiv:f433bdce0fdf582124511d6cb362aee4b0cb992e464c450e3a0149db02b12f79@ec2-52-0-155-79.compute-1.amazonaws.com:5432/dah2hrgpictefi")
db = scoped_session(sessionmaker(bind=engine))

def usertable():
    db.execute("CREATE TABLE userinfo(id SERIAL PRIMARY KEY, fname varchar(70) NOT NULL, email varchar(100) NOT NULL UNIQUE, pwd VARCHAR(50) NOT NULL);")
    print(f"table to store userinfo is created.")
    db.commit()

def bookstable():
    db.execute("CREATE TABLE books(id SERIAL primary key, isbn varchar NOT NULL UNIQUE, title varchar(200) NOT NULL, author VARCHAR(80) NOT NULL, pbyear int not null );")
    print(f"table book's storage is created")
    db.commit()

def reviewtable():
    db.execute("CREATE TABLE reviews(id SERIAL PRIMARY KEY, rating INT, reviews VARCHAR(900) NOT NULL, isbn_no VARCHAR NOT NULL, username VARCHAR(150) NOT NULL, time TIMESTAMP NOT NULL);")
    print(f"table for the reviews is created.") 
    db.commit()

def newisbn():
    db.execute("CREATE TABLE newisbn(id SERIAL primary key, isbn varchar NOT NULL UNIQUE, isbn13 varchar NOT NULL UNIQUE);")
    print(f"table for new isbns is created.")
    db.commit()

def importnewisbn():
    result = db.execute("SELECT * FROM books WHERE id BETWEEN 4001 AND 5000 ORDER BY id").fetchall()                #Please change the values accordingly.
    count = 4001                                                                                                    #This value too.
    for i in result:
        theisbn = i[1]
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"isbns":theisbn})
        if res.status_code == 200:
            details = res.json()["books"][0]
            new_isbn = details["isbn13"]
            if new_isbn is None:
                db.execute("INSERT INTO newisbn(isbn, isbn13) VALUES(:isbn, :new_isbn)",{"isbn":theisbn, "new_isbn":theisbn})
            else:
                db.execute("INSERT INTO newisbn(isbn, isbn13) VALUES(:isbn, :new_isbn)",{"isbn":theisbn, "new_isbn":new_isbn })
            print(f"isbn inserted {count}")
        else:
            print(f"Not Found")
        count += 1
        time.sleep(1)
    print(f"new isbns are added successfully")
    db.commit()

def importbooks():
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader, None)
    count = 0
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books(isbn, title, author, pbyear) VALUES(:isbn, :title, :author, :pbyear)",
                    {"isbn":isbn, "title":title, "author":author, "pbyear":year}
                    )
        print(f"Inserted book {count}")
        count += 1
    print(f"Books added successfully")
    db.commit()


# def authordetails():
#     db.execute("CREATE TABLE author(id SERIAL primary key, authorname varchar(40) NOT NULL, olid VARCHAR(20) NOT NULL UNIQUE, books INT NOT NULL);")
#     print(f"table for author details is created.")
#     db.commit()


# def importauthor():
#     authordata = db.execute("select distinct author, count(*) from books group by author order by count desc limit 10;").fetchall()
#     count = 1
#     for i in authordata:
#         res = requests.get(f"https://openlibrary.org/search/authors.json?q={i.author}")
#         authorid = res.json()["docs"][0]["key"]
#         db.execute("INSERT INTO author(authorname, olid, books) VALUES(:authorname, :olid, :books)",{"authorname": i.author, "olid": authorid, "books": i.count})
#         print(f"author data {count} added.")
#         count += 1
#     db.commit()


def main():
    #Use the function accordingly.
    return authordetails(), importauthor()
    # return usertable(), bookstable(), reviewtable(), importbooks()

if __name__ == '__main__':
    main()
    