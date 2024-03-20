from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import requests
from flask import session, g 
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'key' 
# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

TMDB_API_KEY = 'b6b97675e396833c3d7dbe2acf78bd96'
# Get the current date
current_date = datetime.now().strftime('%Y-%m-%d')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Contact {self.name}>'

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Register')

# Load the movies data
movies_data = pd.read_csv('movies.csv')
second_dataset = pd.read_csv('MoviesOnStreamingPlatforms_updated.csv')

# Perform data preprocessing and cosine similarity calculations
selected_features = ['genres', 'keywords', 'tagline', 'cast', 'director']

# For each feature, fill any missing values (NaN or None) with an empty string ''.
for feature in selected_features:
    movies_data[feature] = movies_data[feature].fillna('')

combined_features = (
    movies_data['genres']
    + ' '
    + movies_data['keywords']
    + ' '
    + movies_data['tagline']
    + ' '
    + movies_data['cast']
    + ' '
    + movies_data['director']
)

vectorizer = TfidfVectorizer()
feature_vectors = vectorizer.fit_transform(combined_features)
similarity = cosine_similarity(feature_vectors)

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/recommend', methods=['POST', 'GET'])
def recommend():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        movie_name = request.form['movie_name']

        # Find a close match for the given movie name
        list_of_all_titles = movies_data['title'].tolist()
        find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)
        if not find_close_match:
            flash('No close match found for the entered movie name.', 'error')
            return redirect(url_for('home'))

        close_match = find_close_match[0]

        # Get the index of the movie in the first dataset
        index_of_the_movie = movies_data[movies_data.title == close_match]['index'].values
        if not index_of_the_movie:
            flash('No movie found for the entered title.', 'error')
            return redirect(url_for('home'))

        index_of_the_movie = movies_data[movies_data.title == close_match]['index'].values[0]

        # Get similarity scores for the movie from the first dataset
        similarity_score = list(enumerate(similarity[index_of_the_movie]))

        # Sort the movies based on similarity score
        sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)

        # Prepare the list of recommended movies with their details (limit to 10)
        recommendations = []

        for movie in sorted_similar_movies[:10]:
            index = movie[0]
            movie_info = movies_data.loc[index]

            # Check if the query result is not empty
            if not movie_info.empty:
                title_from_index = movie_info['title']
                genre_from_index = movie_info['genres']
                director_from_index = movie_info['director']
                tagline_from_index = movie_info['tagline']

                # Look up the corresponding movie in the second dataset
                second_dataset_info = second_dataset[second_dataset['Title'] == title_from_index]

                # Change from checking if a DataFrame is empty using 'if not dataframe.empty:'
                if not second_dataset_info.empty:  
                    imdb_from_second_dataset = second_dataset_info['IMDb'].values[0]
                    ott_from_second_dataset = get_ott_info(second_dataset_info)
                else:
                    # No information found in the second dataset
                    imdb_from_second_dataset = 'NA'
                    ott_from_second_dataset = ['NA']

                recommendations.append(
                    {
                        'title': title_from_index,
                        'genre': genre_from_index,
                        'director': director_from_index,
                        'tagline': tagline_from_index,
                        'imdb': imdb_from_second_dataset,
                        'ott': ott_from_second_dataset,
                    }
                )

        return render_template(
            'index.html', username=session['username'], movie_name=movie_name, recommendations=recommendations
        )

    return render_template('index.html', username=session['username'])

def get_ott_info(row):
    ott_info = []
    if row['Netflix'].values[0] == 1:
        ott_info.append('Netflix')
    if row['Hulu'].values[0] == 1:
        ott_info.append('Hulu')
    if row['Prime Video'].values[0] == 1:
        ott_info.append('Prime Video')
    if row['Disney+'].values[0] == 1:
        ott_info.append('Disney+')
    return ott_info

@app.route('/tmdb')
def tmdb():
    return render_template('tmdb.html')

def get_tmdb_session():
    if 'tmdb_session' not in g:
        g.tmdb_session = requests.Session()
    return g.tmdb_session

@app.route('/get_movie_details', methods=['GET'])
def get_movie_details():
    movie_name = request.args.get('name')
    if not movie_name:
        return render_template('tmdb.html', error='Movie name is required'), 400

    tmdb_session = get_tmdb_session()  # Get the TMDB session
    # Constructing the URL to search for the movie in TMDb API
    search_url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}&language=en-US'

    # Fetching search results from TMDb API
    search_response = tmdb_session.get(search_url)
    if search_response.status_code != 200:
        return render_template('tmdb.html', error='Failed to search for the movie'), search_response.status_code

    search_results = search_response.json().get('results')

    # Checking if any search results are found
    if not search_results:
        return render_template('tmdb.html', error='No movie found with the given name'), 404

    # Considering only the first search result (most relevant)
    movie_id = search_results[0].get('id')

    # Constructing the URL to fetch movie details from TMDb API using the obtained movie ID
    movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US'

    # Fetching movie details from TMDb API
    movie_response = tmdb_session.get(movie_url)
    if movie_response.status_code != 200:
        return render_template('tmdb.html', error='Failed to fetch movie details'), movie_response.status_code

    movie_data = movie_response.json()

    # Extracting relevant movie details
    title = movie_data.get('title')
    overview = movie_data.get('overview')
    release_date = movie_data.get('release_date')
    poster_path = movie_data.get('poster_path')
    popularity = movie_data.get('popularity')
    vote_count = movie_data.get('vote_count')
    video = movie_data.get('video')
    vote_average = movie_data.get('vote_average')
    genres = ", ".join(genre['name'] for genre in movie_data.get('genres'))
    adult = movie_data.get('adult')

    # Constructing the full URL for the poster image with medium size
    if poster_path:
        poster_url = f'https://image.tmdb.org/t/p/w300{poster_path}'  # Using medium size (300px wide)
    else:
        poster_url = None

    # Constructing the movie_details dictionary
    movie_details = {
        'title': title,
        'overview': overview,
        'release_date': release_date,
        'poster_url': poster_url,
        'popularity': popularity,
        'vote_count': vote_count,
        'video': video,
        'vote_average': vote_average,
        'genres': genres,
        'adult': adult
    }
    tmdb_session.close()
    return render_template('tmdb.html', movie_details=movie_details)

from flask import request

@app.route('/recently_released_movies')
def recently_released_movies():
    # Get the TMDB session
    tmdb_session = get_tmdb_session()

    # Parse query parameters for pagination
    page = request.args.get('page', default=1, type=int)
    movies_per_page = 10  # Number of movies per page

    # Calculate the offset based on the page number
    offset = (page - 1) * movies_per_page

    # Constructing the URL to fetch recently released movies from TMDb API
    discover_url = f'https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=en-US&primary_release_date.gte=2022-01-01&primary_release_date.lte={current_date}&sort_by=release_date.desc&with_original_language=en&append_to_response=credits,videos&page={page}'
    discover_response = tmdb_session.get(discover_url)
    if discover_response.status_code != 200:
        return render_template('tmdb.html', error='Failed to fetch recently released movies'), discover_response.status_code

    discover_results = discover_response.json().get('results')

    # Checking if any results are found
    if not discover_results:
        return render_template('tmdb.html', error='No recently released movies found'), 404

    # Extracting relevant movie details for the current page
    recently_released_movies = []
    for movie_data in discover_results[offset:offset + movies_per_page]:
        title = movie_data.get('title')
        overview = movie_data.get('overview')
        release_date = movie_data.get('release_date')
        poster_path = movie_data.get('poster_path')
        imdb_rating = movie_data.get('vote_average')
        
        # Check if 'genres' key is present and not None
        genres = ", ".join(genre['name'] for genre in movie_data.get('genres', []) if genre is not None)
        
        popularity = movie_data.get('popularity')

        # Constructing the full URL for the poster image with medium size
        if poster_path:
            poster_url = f'https://image.tmdb.org/t/p/w300{poster_path}'  # Using medium size (300px wide)
        else:
            poster_url = None

        # Constructing the movie_details dictionary
        movie_details = {
            'title': title,
            'overview': overview,
            'release_date': release_date,
            'poster_url': poster_url,
            'imdb_rating': imdb_rating,
            'genres': genres,
            'popularity': popularity
        }
        recently_released_movies.append(movie_details)

    # Calculate total number of pages for pagination
    total_results = len(discover_results)
    total_pages = (total_results + movies_per_page - 1) // movies_per_page
    return render_template('recently_released_movies.html', recently_released_movies=recently_released_movies, page=page, total_pages=total_pages)
from flask import request

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle form submission
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Store form details in the database
        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()

        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))

    # Render the contact form template
    return render_template('contact.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/users')
def view_users():
    if 'username' not in session:
        return redirect(url_for('login'))
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/contact_details')
def contact_details():
    # Query the database for stored contact details
    contacts = Contact.query.all()

    # Render the template to display contact details
    return render_template('contact_details.html', contacts=contacts)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
