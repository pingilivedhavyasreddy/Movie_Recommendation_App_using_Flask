from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib

app = Flask(__name__)
app.secret_key = 'key'  # Change this to a secure secret key

# Load the movies data
movies_data = pd.read_csv('MoviesOnStreamingPlatforms_updated.csv')

# Perform data preprocessing and cosine similarity calculations
selected_features = ['Genres', 'Country', 'Title', 'Language', 'Directors']

for feature in selected_features:
    movies_data[feature] = movies_data[feature].fillna('')

combined_features = (
    movies_data['Genres']
    + ' '
    + movies_data['Country']
    + ' '
    + movies_data['Title']
    + ' '
    + movies_data['Language']
    + ' '
    + movies_data['Directors']
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

        # Add your authentication logic here
        # For simplicity, let's consider a hardcoded username and password
        if username == 'user' and password == 'key':
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/recommend', methods=['POST', 'GET'])
def recommend():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        movie_name = request.form['movie_name']

        # Find a close match for the given movie name
        list_of_all_titles = movies_data['Title'].tolist()
        find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)
        close_match = find_close_match[0]

        # Get the index of the movie
        index_of_the_movie = movies_data[movies_data.Title == close_match]['ID'].values[0]

        # Get similarity scores for the movie
        similarity_score = list(enumerate(similarity[index_of_the_movie]))

        # Sort the movies based on similarity score
        sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)

        # Prepare the list of recommended movies with their details (limit to 10)
        recommendations = []

        for movie in sorted_similar_movies[:10]:
            index = movie[0]
            title_from_index = movies_data[movies_data.ID == index]['Title'].values[0]

            # Convert the platform values to integers before multiplication
            netflix = int(movies_data[movies_data.ID == index]['Netflix'].values[0])
            hulu = int(movies_data[movies_data.ID == index]['Hulu'].values[0])
            prime_video = int(movies_data[movies_data.ID == index]['Prime Video'].values[0])
            disney_plus = int(movies_data[movies_data.ID == index]['Disney+'].values[0])

            platform_from_index = (
                netflix * 'Netflix' + hulu * 'Hulu' + prime_video * 'Prime Video' + disney_plus * 'Disney+'
            )

            imdb_rating = movies_data[movies_data.ID == index]['IMDb'].values[0]
            rotten_tomatoes_rating = movies_data[movies_data.ID == index]['Rotten Tomatoes'].values[0]
            runtime = movies_data[movies_data.ID == index]['Runtime'].values[0]

            recommendations.append(
                {
                    'title': title_from_index,
                    'platform': platform_from_index,
                    'imdb_rating': imdb_rating,
                    'rotten_tomatoes_rating': rotten_tomatoes_rating,
                    'runtime': runtime,
                }
            )

        return render_template(
            'index.html', username=session['username'], movie_name=movie_name, recommendations=recommendations
        )

    return render_template('index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


