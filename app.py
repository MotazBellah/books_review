from flask import Flask, session, render_template, request, redirect, url_for
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import bs4 as bs
# from urllib.request import urlopen
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

    return render_template('register.html', form=reg_form)

@app.route("/login", methods=['GET', 'POST'])
def login():
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

    return render_template('login.html', form=login_form)


@app.route('/logout')
@login_required
def logout():
    del login_session['user_id']
    return redirect(url_for('register'))


@app.route("/")
def index():
    books = db.execute("SELECT * FROM books limit 20 offset 2").fetchall()
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


@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        name = request.form['name']
        books = db.execute('''SELECT * FROM books WHERE title=:title
                           OR isbn=:isbn OR author=:author;''',
                           {"title": name, "author": name, "isbn": name}).fetchall()
        return render_template('search.html', books=books)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
