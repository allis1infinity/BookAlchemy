import flask
from flask import Flask, render_template, request,  redirect, url_for, flash
import os
from data_models import db, Author, Book
app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config['SECRET_KEY'] = '12345'

db.init_app(app)

# The new route for the homepage.
@app.route('/')
def home():
    # get search and sort parameters from URL
    query = request.args.get("q")       # search text
    sort = request.args.get("sort")     # sorting option

    # start building query
    books_query = Book.query.join(Author)

    # filter books if search text is provided
    if query:
        books_query = books_query.filter(Book.title.contains(query))

    # apply sorting
    if sort == "title":
        books_query = books_query.order_by(Book.title)
    elif sort == "author":
        books_query = books_query.order_by(Author.name)

    # run query
    books = books_query.all()

    if query and not books:
        flash('No books were found for this query 🫣')

    # send books to the template
    return render_template("home.html", books=books)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    # If the request is POST, we need to save the author to the database.
    if request.method == 'POST':
        # Get the author's name from the form.
        name = request.form['name']

        # Get the birthdate and date of death from the form.
        birthdate = request.form['birthdate']
        date_of_death = request.form.get('date_of_death')

        # Create a new Author object with all the data.
        new_author = Author(name=name, birth_date=birthdate,
                            date_of_death=date_of_death)

        # Add the new author to the database and save.
        db.session.add(new_author)
        db.session.commit()

        # Flash a success message
        flash("Author successfully added.")

        return redirect(url_for('add_author'))

    # If the request is GET, render the add_author form.
    return render_template('add_author.html')



@app.route('/add_book', methods=['GET','POST'])
def add_book():
    # If the request is POST, it means the form was submitted.
    if request.method == 'POST':
        # Get data from the form.
        title = request.form['title']
        author_id = request.form['author_id']
        isbn = request.form['isbn']
        publication_year = request.form['publication_year']

        # Create a new Book object with the data.
        new_book = Book(title=title, author_id=author_id,
                        isbn=isbn, publication_year=publication_year)

        # Add the new book to the database and save.
        db.session.add(new_book)
        db.session.commit()

        # Flash a success message
        flash("Book successfully added.")

        return redirect(url_for('add_book'))

    # If the request is GET, we need to pass a list of existing authors to the form.
    # This list will populate the dropdown menu.
    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)

# delete a book by id
@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    # Find the book to delete or return 404 if not found
    book = Book.query.get_or_404(book_id)

    # Store the author's ID before deleting the book
    author_id = book.author_id

    # Delete the book from the database
    db.session.delete(book)
    db.session.commit()

    if Book.query.filter_by(author_id=author_id).count() == 0:
        # If there are no other books, delete the author
        author_to_delete = Author.query.get(author_id)
        if author_to_delete:
            db.session.delete(author_to_delete)
            db.session.commit()
    return redirect(url_for("home"))       # go back to homepage


# with app.app_context():
# db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)