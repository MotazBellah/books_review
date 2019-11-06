import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL = 'postgres://bcuchlesrjetnx:3a811885019d2cedb2a4c32bf93ee63d4ce51e6a844a1818a3d5f585c8c791c2@ec2-54-243-239-199.compute-1.amazonaws.com:5432/d5p4vvbq5jskke'
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()

if __name__ == "__main__":
    main()
