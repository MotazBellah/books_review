from flask import Flask, session, render_template, request, redirect, url_for
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import bs4 as bs
import requests
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
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

@login.user_loader
def load_user(id):
    user_object = db.execute("SELECT * FROM users WHERE id = :id", {"id": int(id)}).fetchone()
    return user_object


@app.route("/register", methods=['GET', 'POST'])
def register():
    try:
        if login_session['user_id']:
            del login_session['user_id']
    except Exception as e:
        pass
    login_session = False
    reg_form = RegistartionForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        email = reg_form.email.data
        password = reg_form.password.data
        hashed_pswd = pbkdf2_sha256.hash(password)
        db.execute("INSERT INTO users (username,email,password) VALUES (:username, :email, :password)",
                   {"username": username, "email": email, "password": hashed_pswd})
        db.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=reg_form, login_session=login_session)

@app.route("/login", methods=['GET', 'POST'])
def login():
    try:
        if login_session['user_id']:
            del login_session['user_id']
    except Exception as e:
        pass
        
    login_session = False

    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        user_object = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone()
        if user_object:
            # login_user(user_object)
            login_session['user_id'] = user_object.id
            return redirect(url_for('index'))
        else:
            return redirect(url_for('register'))

    return render_template('login.html', form=login_form, login_session=login_session)


@app.route('/logout')
def logout():
    if login_session['user_id']:
        del login_session['user_id']
    return redirect(url_for('index'))


@app.route("/")
def index():
    books = db.execute("SELECT * FROM books limit 20 offset 2").fetchall()
    try:
        logged_user = login_session['user_id']
    except Exception as e:
        logged_user = False
    return render_template('index.html', books=books, login_session=logged_user)


@app.route("/<int:book_id>")
def book(book_id):
    try:
        logged_user = login_session['user_id']
        user_rate = db.execute('''SELECT review_count FROM reviews WHERE book_id = :book_id and user_id = :user_id;''',
                              {"book_id": book_id, "user_id": login_session['user_id']}).fetchone()
        if user_rate:
            rate = user_rate.review_count
        else:
            rate = 0
    except Exception as e:
        logged_user = False
        rate = 0

    book_info = db.execute('''SELECT title, author, isbn FROM books WHERE id = :id;''',
                              {"id": book_id}).fetchone()
    comments = db.execute('''SELECT reviews.review_write as coment, users.email as mail, users.username as name FROM reviews JOIN users ON reviews.user_id = users.id AND reviews.book_id = :book_id and review_write IS NOT NULL;''',
                              {"book_id": book_id}).fetchall()

    total_rate = db.execute('''SELECT CAST (sum(review_count) as DOUBLE PRECISION) / CAST(count(id) as DOUBLE PRECISION) as total_rating FROM reviews WHERE book_id = :book_id;''',
                          {"book_id": book_id}).fetchone()
    if total_rate:
        total = total_rate.total_rating
    else:
        total = 0

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "uXFuECWGEsTMTQS5ETg", "isbns": "{}".format(book_info.isbn)})
    print(res.json()['books'][0]['average_rating'])
    print("===========")
    rating = res.json()['books'][0]['average_rating']
    # users = db.execute('''SELECT username FROM users WHERE id IN :id;''',
    #                       {"id": list(comments.user_id)}).fetchall()

    source = urlopen('https://www.goodreads.com/book/isbn/{}?key=uXFuECWGEsTMTQS5ETg'.format(book_info.isbn)).read()
    soup = bs.BeautifulSoup(source, 'lxml')
    description = soup.find('book').find('description')
    img_url = "http://covers.openlibrary.org/b/isbn/{}-L.jpg".format(book_info.isbn)
    print(description.text)
    # if cube:
    return render_template('book.html', total_rate=total, user_rate=rate, rating=rating, login_session=logged_user, comments=comments, description=description.text, img_url=img_url, book_title=book_info.title, book_author=book_info.author, book_id=book_id)



@app.route("/rate/<int:user_id>/<int:book_id>")
def rate(user_id, book_id):
    value = request.args['value']
    # db.execute("INSERT INTO reviews (review_count) VALUES (:value) WHERE book_id= :book_id and user_id = :user_id;",
    #           {"value": int(value), "user_id":user_id, "book_id":book_id})
    user_rate = db.execute('''SELECT * FROM reviews WHERE book_id = :book_id and user_id = :user_id;''',
                          {"book_id": book_id, "user_id": user_id}).fetchone()
    if user_rate:
        db.execute("UPDATE reviews SET review_count = :value WHERE book_id= :book_id and user_id = :user_id;",
                  {"value": int(value), "user_id":user_id, "book_id":book_id})
    else:
        db.execute('''INSERT INTO reviews (review_count, book_id, user_id) VALUES (:review_count, :book_id, :user_id);''',
                  {"review_count": value, "book_id": book_id, "user_id": login_session['user_id']})

    db.commit()
    return redirect(url_for('book', book_id=book_id))


@app.route("/comment/<int:user_id>/<int:book_id>", methods=['GET', 'POST'])
def comment(book_id, user_id):
    if request.method == 'POST':
        comment = request.form['name']
        user_rate = db.execute('''SELECT * FROM reviews WHERE book_id = :book_id and user_id = :user_id;''',
                              {"book_id": book_id, "user_id": user_id}).fetchone()
        if user_rate:
            db.execute("UPDATE reviews SET review_write = :review_write WHERE book_id= :book_id and user_id = :user_id;",
                    {"review_write": comment, "user_id":user_id, "book_id":book_id})
        else:
            db.execute('''INSERT INTO reviews (review_write, book_id, user_id) VALUES (:review_write, :book_id, :user_id);''',
                  {"review_write": comment, "book_id": book_id, "user_id": login_session['user_id']})

        db.commit()
        return redirect(url_for('book', book_id=book_id))


@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        name = request.form['name']
        books = db.execute('''SELECT * FROM books WHERE title ILIKE '%{}%'
                           OR isbn ILIKE '%{}%' OR author ILIKE '%{}%';'''.format(name, name, name)).fetchall()

        return render_template('search.html', books=books, login_session=login_session)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
