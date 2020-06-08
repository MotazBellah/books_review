from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import bs4 as bs
import requests
import json
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
# To make sure the code is correct with python 2.x and 3.x
try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

from wtform_fields import *

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['WTF_CSRF_SECRET_KEY'] = "b'f\xfa\x8b{X\x8b\x9eM\x83l\x19\xad\x84\x08\xaa"


# Set up database
DATABASE_URL = 'postgres://bcuchlesrjetnx:3a811885019d2cedb2a4c32bf93ee63d4ce51e6a844a1818a3d5f585c8c791c2@ec2-54-243-239-199.compute-1.amazonaws.com:5432/d5p4vvbq5jskke'
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

# configure flask_login
login = LoginManager()
login.init_app(app)
# app.config['LOGIN_DISABLED'] = False

# manage a database connection
# To avaid time errors
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()


@login.user_loader
def load_user(id):
    user_object = db.execute("SELECT * FROM users WHERE id = :id", {"id": int(id)}).fetchone()
    return user_object


# Register route, render the form and validate the register form
@app.route("/register", methods=['GET', 'POST'])
def register():
    # Make sure the user_id not in session
    try:
        if login_session['user_id']:
            del login_session['user_id']
    except Exception as e:
        pass
    login_session = False
    # load the registration form from the wtform_fields
    reg_form = RegistartionForm()
    if reg_form.validate_on_submit():
        # get the data from each field
        username = reg_form.username.data
        email = reg_form.email.data
        password = reg_form.password.data
        # use passlib.hash to hash the password
        hashed_pswd = pbkdf2_sha256.hash(password)
        # load the data into users table, then redirect to login page
        db.execute("INSERT INTO users (username,email,password) VALUES (:username, :email, :password)",
                   {"username": username, "email": email, "password": hashed_pswd})
        db.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=reg_form, login_session=login_session)


# Login route, render the form and validate the login form
@app.route("/login", methods=['GET', 'POST'])
def login():
    #  Make sure there is no user logged in
    try:
        if login_session['user_id']:
            del login_session['user_id']
    except Exception as e:
        pass
    # load the login form from the wtform_fields
    login_form = LoginForm()
    if login_form.validate_on_submit():
        # get the data and check if the user is Registered
        email = login_form.email.data
        user_object = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone()
        if user_object:
            login_session['user_id'] = user_object.id
            return redirect(url_for('index'))
        else:
            return redirect(url_for('register'))

    return render_template('login.html', form=login_form, login_session='')


# Logout route, delete the user_id
@app.route('/logout')
def logout():
    if login_session['user_id']:
        del login_session['user_id']
    return redirect(url_for('index'))


# Main route, render some books on the page
# Make suer if the user is logged in to display the search bar
@app.route("/")
def index():
    books = db.execute("SELECT * FROM books limit 20 offset 2").fetchall()
    try:
        logged_user = login_session['user_id']
    except Exception as e:
        logged_user = False
    return render_template('index.html', books=books, login_session=logged_user)


# Book info route,display the book information(goodreads rating, image, description)
# allow the user to set the rating and write reviews and read other user's reviews
@app.route("/<int:book_id>")
def book(book_id):
    # If user logged in, render the rate and comment forms
    # allow the user to set the rating and write a comment
    rate = 0
    if 'user_id' in login_session:
        logged_user = login_session['user_id']
        user_rate = db.execute('''SELECT review_count FROM reviews WHERE book_id = :book_id and user_id = :user_id;''',
                              {"book_id": book_id, "user_id": login_session['user_id']}).fetchone()

        if user_rate:
            if user_rate.review_count:
                rate = user_rate.review_count
    else:
        logged_user = False

    # get the book information to use it in the html page
    book_info = db.execute('''SELECT title, author, isbn, year FROM books WHERE id = :id;''',
                              {"id": book_id}).fetchone()
    # get all reviews from all users and send it to html page
    comments = db.execute('''SELECT reviews.review_write as coment, users.email as mail, users.username as name
                          FROM reviews JOIN users ON reviews.user_id = users.id AND
                          reviews.book_id = :book_id and review_write IS NOT NULL;''',
                          {"book_id": book_id}).fetchall()
    # calculate the total rate for each book
    total_rate = db.execute('''SELECT CAST (sum(review_count) as DOUBLE PRECISION) / CAST(count(id) as DOUBLE PRECISION)
                            as total_rating FROM reviews WHERE book_id = :book_id;''',
                           {"book_id": book_id}).fetchone()
    # if found a total rate, i.e if some user set rating, then round it to 2
    if total_rate.total_rating:
        total = round(total_rate.total_rating, 2)
    else:
        total = 0

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "uXFuECWGEsTMTQS5ETg", "isbns": "{}".format(book_info.isbn)})
    goodreads_rating = res.json()['books'][0]["average_rating"]
    goodreads_rating_count = res.json()['books'][0]["ratings_count"]

    # send get request to get the information of each book from goodreads API
    # The response in XML format
    source = urlopen('https://www.goodreads.com/book/isbn/{}?key=uXFuECWGEsTMTQS5ETg'.format(book_info.isbn)).read()
    # Use BeautifulSoup to parse the xml response
    soup = bs.BeautifulSoup(source, 'lxml')
    # get the description
    description = soup.find('book').find('description')
    # Use openlibrary API tp get the image of each book
    img_url = "http://covers.openlibrary.org/b/isbn/{}-L.jpg".format(book_info.isbn)

    return render_template('book.html', total_rate=total, user_rate=rate, rating=goodreads_rating, count=goodreads_rating_count,
                           login_session=logged_user, comments=comments, description=description.text, isbn=book_info.isbn, year=book_info.year,
                           img_url=img_url, book_title=book_info.title, book_author=book_info.author, book_id=book_id)


@app.route('/book-rate', methods=['POST'])
def rate_book():
    rate = request.form['rating']
    book_id = request.form['book_id']

    # check if the user write a review or rating for this book
    user_rate = db.execute('''SELECT review_count, review_write FROM reviews WHERE book_id = :book_id and user_id = :user_id;''',
                          {"book_id": book_id, "user_id": login_session['user_id']}).fetchone()
    # check if the user write a review or rating for this book
    if user_rate:
        # If the user already gave rating then return and inform the user
        if user_rate.review_count:
            return jsonify({'error': 'You already rated this book'})
        # If the user write a review for the book,
        #  then update the table by adding the value of the rating
        else:
            db.execute("UPDATE reviews SET review_count = :value WHERE book_id= :book_id and user_id = :user_id;",
                      {"value": int(rate), "user_id":login_session['user_id'], "book_id":book_id})
    # If not, then insert the value of the rating
    else:
        db.execute('''INSERT INTO reviews (review_count, book_id, user_id) VALUES (:review_count, :book_id, :user_id);''',
                  {"review_count": int(rate), "book_id": book_id, "user_id": login_session['user_id']})


    db.commit()

    # calculate the total rate for each book
    total_rate = db.execute('''SELECT CAST (sum(review_count) as DOUBLE PRECISION) / CAST(count(id) as DOUBLE PRECISION)
                            as total_rating FROM reviews WHERE book_id = :book_id;''',
                           {"book_id": book_id}).fetchone()

    # if found a total rate, i.e if some user set rating, then round it to 2
    if total_rate.total_rating:
        total = round(total_rate.total_rating, 2)
    else:
        total = 0

    return jsonify({
        'rate': rate,
        'book_id': book_id,
        'total_rate': total
    })


# Get the book id and user id to write a review
@app.route("/comment/<int:user_id>/<int:book_id>", methods=['GET', 'POST'])
def comment(book_id, user_id):
    if request.method == 'POST':
        # get the value from the form
        comment = request.form['name']
        # check if the user write a review or rating for this book
        user_rate = db.execute('''SELECT * FROM reviews WHERE book_id = :book_id and user_id = :user_id;''',
                              {"book_id": book_id, "user_id": user_id}).fetchone()
        # If the user set the rating for the book,
        # then update the table by adding the value of the review
        if user_rate:
            db.execute("UPDATE reviews SET review_write = :review_write WHERE book_id= :book_id and user_id = :user_id;",
                    {"review_write": comment, "user_id":user_id, "book_id":book_id})
        # If not, then insert the value of the review
        else:
            db.execute('''INSERT INTO reviews (review_write, book_id, user_id) VALUES (:review_write, :book_id, :user_id);''',
                  {"review_write": comment, "book_id": book_id, "user_id": login_session['user_id']})

        db.commit()
        return redirect(url_for('book', book_id=book_id))


# Get the book id and user id to write a review
@app.route("/comment-book", methods=['POST'])
def comment_book():
    if request.method == 'POST':
        # get the value from the form
        comment = request.form['value']
        book_id = request.form['book_id']
        # check if the user write a review or rating for this book
        user_rate = db.execute('''SELECT * FROM reviews WHERE book_id = :book_id and user_id = :user_id;''',
                              {"book_id": book_id, "user_id": login_session['user_id']}).fetchone()
        # If the user set the rating for the book,
        # then update the table by adding the value of the review
        if user_rate:
            db.execute("UPDATE reviews SET review_write = :review_write WHERE book_id= :book_id and user_id = :user_id;",
                    {"review_write": comment, "user_id":login_session['user_id'], "book_id":book_id})
        # If not, then insert the value of the review
        else:
            db.execute('''INSERT INTO reviews (review_write, book_id, user_id) VALUES (:review_write, :book_id, :user_id);''',
                  {"review_write": comment, "book_id": book_id, "user_id": login_session['user_id']})

        db.commit()

        # get all reviews from all users and send it to html page
        comments = db.execute('''SELECT reviews.review_write as coment, users.email as mail, users.username as name
                              FROM reviews JOIN users ON reviews.user_id = :user_id AND
                              reviews.book_id = :book_id and review_write IS NOT NULL;''',
                              {"book_id": book_id, "user_id": login_session['user_id']}).fetchall()
        print('HHHHHHHHHHH')
        print(comments)
        if comments:
            # Convert the comments resut to a plain list of dicts
            user_comment = [dict(comment.items()) for comment in comments]
        else:
            user_comment = []
        print(user_comment)
        print('???????????????????')
        if user_comment:
            return jsonify({'comment': user_comment})
        return jsonify({'error': "something went wrong!"})


# # search using title, isbn or auther
# @app.route("/search", methods=['GET', 'POST'])
# def search():
#     if request.method == 'POST':
#         name = request.form['name']
#         books = db.execute('''SELECT * FROM books WHERE title ILIKE '%{}%'
#                            OR isbn ILIKE '%{}%' OR author ILIKE '%{}%';'''.format(name, name, name)).fetchall()
#
#         return render_template('search.html', books=books, login_session=login_session)


# search using title, isbn or auther
@app.route("/search-books", methods=['POST'])
def search_books():
    if request.method == 'POST':
        name = request.form['name']
        # Check if the input is valid
        if len(name) == 0 or name.isspace():
            return jsonify({'error': 'There are no books!'})

        books = db.execute('''SELECT * FROM books WHERE title ILIKE '%{}%'
                           OR isbn ILIKE '%{}%' OR author ILIKE '%{}%';'''.format(name, name, name)).fetchall()

        if books:
            # Convert the books resut to a plain list of dicts
            searched_books = [dict(book.items()) for book in books]
        else:
            searched_books = []
        print(searched_books)
        print('???????????????????')
        if searched_books:
            return jsonify({'books': searched_books})
        return jsonify({'error': 'There are no books!'})


@app.route("/api/<isbn>", methods=['GET'])
def book_api(isbn):
    book = db.execute('''SELECT * FROM books WHERE isbn = :isbn;''',
                     {"isbn": isbn}).fetchone()
    if book:
        total_rate = db.execute('''SELECT sum(review_count) as total_rating, count(*) as count FROM reviews WHERE book_id = :book_id;''',
                               {"book_id": book.id}).fetchone()

        if total_rate.total_rating:
            count = total_rate.count
            avg = total_rate.total_rating / count
            average_score = round(avg, 2)
        else:
            average_score = 0
            count = 0

        return jsonify({
                "title": book.title,
                "author": book.author,
                "year": book.year,
                "isbn": book.isbn,
                "review_count": count,
                "average_score": average_score
            })
    else:
         return jsonify({"error": "Invalid book"}), 422






if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
