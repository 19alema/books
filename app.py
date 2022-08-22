# -------------------------------------------------------------------
# App Imports
# -------------------------------------------------------------------
from email.policy import default
import config
from flask import Flask, session
# from flask.ext.session import Session
from flask import  url_for, Flask, redirect,request,render_template,flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


basedir = os.path.abspath(os.path.dirname(__file__))
# CONFIGURATION OF THE APP
app = Flask(__name__, static_url_path='/static')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.config.from_object(config)
SESSION_TYPE = 'redis'
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
# Session(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:19alema@localhost:5432/library" # APP DATABASE URI

#=========================================================================
# MODELS
#=========================================================================

# LIBRARY
class Library(db.Model):
    __tablename__ = 'library'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    city = db.Column(db.String(250), nullable=False) 
    website = db.Column(db.String(250))
    image = db.Column(db.String(1000), nullable=False)
    address = db.Column(db.String(250), nullable=False)

    books = db.relationship('Books', backref="books", lazy=True)

    def __repr__(self):
      return f"<id: {self.id} name: {self.name}>"

# AUTHORS
class Authors(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    nationality = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    biography = db.Column(db.String(3050), nullable=False)

    publications = db.relationship('Books', backref="book", lazy=True)

    def __repr__(self):
      return f"<id {self.id} name: {self.name}>"
# BOOKS
class Books(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    book_image = db.Column(db.String(800), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(200),nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    publication_date = db.Column(db.String(100), nullable=False)
    book_status = db.Column(db.Boolean, nullable=True, default=False)
    description = db.Column(db.String(1000), nullable=False)

    location = db.Column(db.Integer, db.ForeignKey('library.id'), nullable=False)
    auther = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    def __repr__(self):
      return f"<books {self.id} name: {self.title}>"
db.create_all()
# Routes and Controllers

#==========================================================================
# HOME PAGE
# =========================================================================
@app.route('/', methods=['GET'])
def home_page():
    return render_template('pages/index.html')

#==========================================================================
# Books
#==========================================================================

@app.route('/books')
def get_books():
    books = Books.query.all()
 
    data = []
    for book in books:
        author= Authors.query.get(book.auther)
        
        if book.rating > 1000:
            rating =str(int(book.rating) / 1000) + 'k'
        else: 
            rating= book.rating 
        data.append({
                'id': book.id,
                'title': book.title,
                'image_link': book.book_image,
                'genre': book.genre,
                'pages': book.pages,
                'publication': book.publication_date,
                'overview': book.description,
                'status': book.book_status,
                'ratings': rating,
                'author': author.name,
                'author_id': author.id

            })

    return render_template('pages/books.html', books = data)
#==========================================================================
#  Authers
#==========================================================================

@app.route('/author')
def get_authers():
    data =[]
    authors = Authors.query.all()
    for author in authors:
        data.append({
            "id": author.id,
            "name": author.name
        })

    return render_template('pages/auther.html', data = data)

#==========================================================================
# Libraries
#==========================================================================

@app.route('/location')
def get_libraries():
    data =[]
    locations = Library.query.all()
    for location in locations:
        data.append({
            "id": location .id,
            "name": location .name
        })

    return render_template('pages/library.html', data = data)




#========================================================================
# SINGLE BOOKS, AUTHORS AND LIBRARY DETAILS
#=========================================================================
# ABOUT SINGLE BOOK

@app.route('/books/book/<book_id>', methods=['GET'])
def book_detail(book_id):
     return book_id


# SINGLE AUTHOR
@app.route('/authors/author/<author_id>', methods=['GET'])
def author_info(author_id):
    auther_data = []
    publication =[]
    auther = Authors.query.get(author_id)
    book = Books.query.filter_by(auther = auther.id).all()

    print(book)
    for book in book:
        print(book.id)
        publication.append({
        'title': book.title,
        'image':book.book_image,
        'id':book.id
    })

    auther_data.append({
        'image_link': auther.image,
        'name':auther.name,
        'bio':auther.biography,
        'books': publication,
        'nationality':auther.nationality,
        'email':auther.email,
        'id':auther.id,
        'total_books': len(publication)
    })
   
    print(publication)
          
   

    return render_template('/pages/single_auther.html', auther_data=auther_data)

# SINGLE LOCATION 

@app.route('/locs/loc/<loc_id>', methods=['GET'])
def single_location(loc_id):
    books_data=[]
    loc_data=[]
    loc = Library.query.get(loc_id);

    loc_books=Books.query.filter_by(location=loc_id).all()

    for book in loc_books:
        print(book.id)

        book_author=Authors.query.filter_by(id=book.auther).all()

        for author in book_author:
            print(author.name)

      
        books_data.append({
            'title':book.title,
            'author':author.name,
            'id':book.id,
            'author_id': author.id
        })

    loc_data.append({
        'id':loc.id,
        'image':loc.image,
        'name':loc.name,
        'city':loc.city,
        'website':loc.website,
        'address':loc.address,
        'books':books_data,
        'total_books':len(books_data)
    })
    
    print(book_author)


    return render_template('pages/single_library.html', locs=loc_data)
# EDIT AUTHOR
@app.route('/author/<author_id>/edit', methods=['GET','POST'])
def edit_author(author_id):
    authors = Authors.query.get(author_id)
    if request.method == 'GET':
        
        image = authors.image
        name=authors.name
        email = authors.email
        biography=authors.biography
        nationality=authors.nationality
        id=authors.id

        authors={
            'id':id,
            'image':image,
            'name':name,
            'biography':biography,
            'email':email,
            'nationality':nationality
        }

        print(authors)

        return render_template('forms/edit_auther.html', author=authors)
    else:

        try:
            authors.image = request.form.get('image'),
            authors.name = request.form.get('name'),
            authors.nationality=request.form.get('nationality'),
            authors.email = request.form.get('email'),
            authors.biography=request.form.get('biography')
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.close()
        return redirect(url_for('get_authers'))


    return 'Hello'



#========================================================================
# CREATE BOOKS, AUTHORS AND LIBRARY DETAILS
#=========================================================================
#CREAT ABOUT SINGLE BOOK

@app.route('/book/create', methods=['GET','POST'])
def create_book():
    if request.method == 'GET':
        return render_template('forms/new_book.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        image= request.form.get('image')
        pages= request.form.get('page')
        status= True if request.form.get('status')=='on' else False
        location= request.form.get('location')
        description= request.form.get('description')
        author= request.form.get('authors')
        date= request.form.get('date')
        genre= request.form.get('genre')
        rating= request.form.get('rating')

        try:
            newBook = Books(
                book_image=image,
                title=title,
                pages =pages,
                book_status=status,
                description=description,
                publication_date = date,
                auther = author,
                location = location,
                genre=genre,
                rating=rating
            )
            db.session.add(newBook)
            db.session.commit()
            flash("Book has been added")
           
        except Exception as e:
            print(e)
            flash("Book not added error")
            db.session.rollback()
        finally:
            db.session.close() 

        return render_template('pages/index.html')


# CREATE AUTHOR
@app.route('/author/create', methods=['GET', 'POST'])
def create_author():
    if request.method == 'GET':

        return render_template('/forms/new_auther.html')
    else:

        try:
            newAuthor=Authors(
                image = request.form.get('image'),
                name = request.form.get('name'),
                nationality=request.form.get('nationality'),
                email = request.form.get('email'),
                biography=request.form.get('biography')
            )
            db.session.add(newAuthor)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return redirect(url_for('get_authers'))
#=======================================================
# EDIT BOOK
#=======================================================
@app.route('/book/<book_id>/edit', methods=['GET', 'POST'])

def update_Book(book_id):
    book = Books.query.get(book_id)
    author = Authors.query.get(book.auther)
 
    if request.method == 'GET':
        title=book.title
        id=book.id
        book_image=book.book_image
        genre=book.genre
        pages=book.pages
        rating=book.rating
        publication=book.publication_date
        status=book.book_status
        description=book.description
        location=book.location
        auther=book.auther
   

        books={
            'id':id,'title':title,'location':location,
            'description':description,'status':status,
            'pages':pages,'ratings':rating,
            'genre':genre,'publication':publication,
            'book_image':book_image, 'author':auther
        }
        print(books)

        return render_template('/forms/edit_book.html', book=books, author=author)
    else:
        

        try:
            book = Books.query.get(book_id)
            book.title = request.form.get('title')
            book.description = request.form.get('overview')
            book.pages = request.form.get('pages')
            book.rating = request.form.get('ratings')
            book.book_image= request.form.get('image_link')
            book.publication_date = request.form.get('publication')
            book.auther = request.form.get('author')
            book.book_status = True if request.form.get('status') == 'on' else False
            book.genre = request.form.get('genre')
            book.location = request.form.get('location')
            # book.title = request.form.get('title')
            db.session.commit()
            print(book)
        except Exception as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.close()
        return redirect(url_for('get_books'))

      
#=======================================================
# DELETE BOOK
#=======================================================
@app.route('/book/<book_id>/delete', methods=['DELETE','GET'])
def remove_book(book_id):

    
    if request.method=='GET': 
        return redirect(url_for('home_page')) 
    elif request.method=='DELETE':  
        try:
            book= Books.query.get(book_id)

            print(book)
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.close()

        return jsonify({
            'success':True
        })













































if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost', port=5000)