from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
DATABASE_URL = 'postgres://bcuchlesrjetnx:3a811885019d2cedb2a4c32bf93ee63d4ce51e6a844a1818a3d5f585c8c791c2@ec2-54-243-239-199.compute-1.amazonaws.com:5432/d5p4vvbq5jskke'
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    books = db.execute("SELECT * FROM books limit 10 offset 2").fetchall()
    return render_template('index.html', books=books)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0')
