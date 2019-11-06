import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL = 'postgres://bcuchlesrjetnx:3a811885019d2cedb2a4c32bf93ee63d4ce51e6a844a1818a3d5f585c8c791c2@ec2-54-243-239-199.compute-1.amazonaws.com:5432/d5p4vvbq5jskke'
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

def main():
    commands = (
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE,
            password VARCHAR(255) NOT NULL
        )
        """,
        """ CREATE TABLE books (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                year INTEGER NOT NULL,
                isbn VARCHAR(255) NOT NULL
        )
        """,
        """ CREATE TABLE reviews (
                id SERIAL PRIMARY KEY,
                book_id INTEGER REFERENCES books(id),
                user_id INTEGER REFERENCES users(id),
                review_write VARCHAR(255),
                review_count INTEGER,
                average_score NUMERIC
        )
        """

        )
    for command in commands:
        db.execute(command)
    db.commit()

if __name__ == "__main__":
    main()
