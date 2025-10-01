from flask import Flask, render_template, request,  redirect, url_for, flash
from dotenv import load_dotenv
import os
from data_models import db, Author, Book
from datetime import datetime

load_dotenv()
app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)

def validate(form, required_fields):
    """Returns True if all required fields are present and not empty."""
    return all(form.get(field) for field in required_fields)


@app.route('/')
def home():
    """Renders the homepage, handling search and sort parameters for the book list."""

    query = request.args.get("q")
    sort = request.args.get("sort")

    books_query = Book.query.join(Author)

    # filter books if search text is provided
    if query:
        books_query = books_query.filter(Book.title.contains(query))

    if sort == "title":
        books_query = books_query.order_by(Book.title)
    elif sort == "author":
        books_query = books_query.order_by(Author.name)


    books = books_query.all()

    if query and not books:
        flash('No books were found for this query 🫣')

    return render_template("home.html", books=books)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Handles adding a new author."""

    if request.method == 'POST':
        name = request.form.get("name")
        birthdate_str = request.form.get("birth_date")
        date_of_death_str = request.form.get("date_of_death")

        if not validate(request.form, ["name", "birth_date"]):
            flash("Name and Birthdate are required!", "error")
            return redirect(url_for("add_author"))

        try:
            format_birth_date = datetime.strptime(birthdate_str,'%Y-%m-%d').date()
            format_date_of_death = None
            if date_of_death_str:
                format_date_of_death = datetime.strptime(date_of_death_str,
                                                      '%Y-%m-%d').date()

            new_author = Author(
                name=name,
                birth_date=format_birth_date,
                date_of_death=format_date_of_death
            )
            db.session.add(new_author)
            db.session.commit()
            flash("Author successfully added.")
            return redirect(url_for('add_author'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding author: {e}", "error")
            return redirect(url_for("add_author"))

    # If the request is GET, render the add_author form.
    return render_template('add_author.html')


@app.route('/add_book', methods=['GET','POST'])
def add_book():
    """Handles adding a new book via GET (form) and POST (save to database)."""
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
        try:
            db.session.add(new_book)
            db.session.commit()
            # Flash a success message
            flash("Book successfully added.")
        except Exception as e:
            # Flash an error message
            flash(f"Error adding author: {e}", "error")

        return redirect(url_for('add_book'))

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """Deletes a book by its ID and removes the author if no other books exist."""

    book = Book.query.get_or_404(book_id)
    author_id = book.author_id

    db.session.delete(book)
    db.session.commit()

    message = "Book deleted successfully!"

    if Book.query.filter_by(author_id=author_id).count() == 0:
        # If there are no other books, delete the author
        author_to_delete = Author.query.get(author_id)
        if author_to_delete:
            db.session.delete(author_to_delete)
            db.session.commit()
            message = "Book and author deleted successfully!"
    flash(message, "success")
    return redirect(url_for("home"))


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)