import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def usertable():
    db.execute("CREATE TABLE userinfo( fname varchar(70) NOT NULL, email varchar(150) PRIMARY KEY NOT NULL, pwd VARCHAR(50) NOT NULL);")
    print(f"table to store userinfo is created.")
    db.commit()

def bookstable():
    db.execute("CREATE TABLE books( isbn_no varchar primary key NOT NULL, title varchar(200) NOT NULL, author VARCHAR(80) NOT NULL, pbyear int not null );")
    print(f"table book's storage is created")
    db.commit()

def reviewtable():
    db.execute("CREATE TABLE reviews(isbn_no varchar not null, email varchar(150) not null, rating int, reviews varchar(700));")
    print(f"table for the reviews is created.")
    db.commit()

def importbooks():
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader, None)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books(isbn_no, title, author, pbyear) VALUES(:isbn_no, :title, :author, :pbyear)",
                    {"isbn_no":isbn, "title":title, "author":author, "pbyear":year}
                    )
    print(f"Books added successfully")
    db.commit()


def main():
    return usertable(), bookstable(), reviewtable(), importbooks()

if __name__ == '__main__':
    main()
    