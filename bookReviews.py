from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
db = SQLAlchemy(app)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(200), index=True, nullable=False)
    review_text = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Integer, index=True, nullable=False) 

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add-review', methods=['GET', 'POST'])
def add_review():
    if request.method == 'POST':
        book_title = request.form['book_title']
        review_text = request.form['review_text']
        rating = int(request.form['rating'])
        
        new_review = Review(book_title=book_title, review_text=review_text, rating=rating)
        
        db.session.add(new_review)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('add_review.html')

@app.route('/all-reviews')
def all_reviews():
    reviews = Review.query.all()
    return render_template('all_reviews.html', reviews=reviews)

@app.route('/edit-review/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)
    if request.method == 'POST':
        review.book_title = request.form['book_title']
        review.review_text = request.form['review_text']
        review.rating = int(request.form['rating'])
        db.session.commit()
        return redirect(url_for('all_reviews'))
    return render_template('edit_review.html', review=review)

@app.route('/delete-review/<int:review_id>')
def delete_review(review_id):
    review_to_delete = Review.query.get_or_404(review_id)
    db.session.delete(review_to_delete)
    db.session.commit()
    return redirect(url_for('all_reviews'))

@app.route('/generate-report', methods=['GET', 'POST'])
def generate_report():
    book_titles = Review.query.with_entities(Review.book_title).distinct().all()
    ratings = Review.query.with_entities(Review.rating).distinct().all()

    if request.method == 'POST':
        selected_title = request.form.get('book_title')
        selected_rating = request.form.get('rating')

        base_query = "SELECT * FROM review WHERE 1=1"
        parameters = {}
        if selected_title and selected_title != 'All':
            base_query += " AND book_title = :book_title"
            parameters['book_title'] = selected_title
        if selected_rating and selected_rating != 'All':
            base_query += " AND rating = :rating"
            parameters['rating'] = int(selected_rating)

        query = text(base_query)
        result = db.session.execute(query, parameters)
        reviews = result.fetchall()
        return render_template('report.html', reviews=reviews)

    return render_template('report_form.html', book_titles=book_titles, ratings=ratings)
if __name__ == "__main__":
    app.run(debug=True)