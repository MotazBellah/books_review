from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
import bs4 as bs
# from urllib.request import urlopen
from urllib import urlopen

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
    print(books)
    return render_template('index.html', books=books)


@app.route("/<book_isbn>")
def book(book_isbn):
    book_info = db.execute('''SELECT title, author, id FROM books WHERE isbn = :isbn;''',
                              {"isbn": book_isbn}).fetchall()
    # print(book_info[0][0])
    source = urlopen('https://www.goodreads.com/book/isbn/{}?key=uXFuECWGEsTMTQS5ETg'.format(book_isbn)).read()
    soup = bs.BeautifulSoup(source, 'lxml')
    description = soup.find('book').find('description')
    img_url = "http://covers.openlibrary.org/b/isbn/{}-L.jpg".format(book_isbn)
    print(description.text)
    # if cube:
    return render_template('book.html', description=description.text, img_url=img_url, book_title=book_info[0][0], book_author=book_info[0][1], book_id=book_info[0][2])



@app.route("/rate/<int:book_id>")
def rate(book_id):
    value = request.args['value']
    return str(book_id) + ' ' + str(value)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(debug=True, host='0.0.0.0')
