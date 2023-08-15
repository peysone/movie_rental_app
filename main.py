import requests
from flask import Flask, render_template, request
"""
aplikacja do obsługi wypożyczalni filmów, korzystająca z API serwisu TMDB
"""
app = Flask(__name__)

class VideoRentalDatabase:
    def __init__(self):
        self.movies = {}
        self.load_rented_movies()

    def load_rented_movies(self):
        try:
            with open('rented_movies.txt', 'r') as file:
                for line in file:
                    title = line.strip()
                    self.movies[title] = {"is_rented": True}
        except FileNotFoundError:
            pass

    def save_rented_movies(self):
        with open('rented_movies.txt', 'w') as file:
            for title, info in self.movies.items():
                if info["is_rented"]:
                    file.write(f"{title}\n")
    #zapisywanie do pliku aktualnie wypozyczonych filmów
    def rent_movie(self, title):
        if title in self.movies and not self.movies[title]["is_rented"]:
            self.movies[title]["is_rented"] = True
            self.save_rented_movies()
            self.log(f"Użytkownik wypożyczył film: {title}")
            return f"Film '{title}' został wypożyczony. Miłego seansu!"
        return f"Film '{title}' jest niedostępny lub już został wypożyczony."
    # sprawdzanie czy film został wypożyczony i poinformowanie użytkownika o możliwości wypożyczenia

    def return_movie(self, title):
        if title in self.movies and self.movies[title]["is_rented"]:
            self.movies[title]["is_rented"] = False
            self.save_rented_movies()
            self.log(f"Użytkownik zwrócił film: {title}")
            return f"Dziękujemy za zwrot filmu '{title}'."
        return f"Film '{title}' nie został wypożyczony z tego sklepu."
    # sprawdzenie czy dany film został wypożyczony z naszej wypożyczalni, nastepnie możliwy zwrot filmu
    def check_availability(self, title):
        if title in self.movies:
            if self.movies[title]["is_rented"]:
                return f"Film '{title}' jest obecnie wypożyczony."
            return f"Film '{title}' jest dostępny do wypożyczenia."
        return f"Film '{title}' nie istnieje w naszej bazie danych."
    # sprawdzenie dostępności filmu do wypożyczenia
    def log(self, message):
        with open('rental_actions.log', 'a') as log_file:
            log_file.write(message + '\n')

rental_database = VideoRentalDatabase()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rent', methods=['POST'])
def rent_movie():
    film_title = request.form['rent_film']
    result = rental_database.rent_movie(film_title)
    return render_template('index.html', result=result, show_back_button=True)


@app.route('/return', methods=['POST'])
def return_movie():
    film_title = request.form['return_film']
    result = rental_database.return_movie(film_title)
    print(f"Value of 'result': {result}")
    return render_template('index.html', result=result)


@app.route('/availability', methods=['POST'])
def check_availability():
    film_title = request.form['check_availability']
    result = rental_database.check_availability(film_title)
    print(f"Value of 'result': {result}")
    return render_template('index.html', result=result)

@app.route('/run_code', methods=['POST'])
def run_code():
    film_title = request.form['film_title']

    tmdb_api_key = "5ccd7607ff252b40eb732caef2bd2014"
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={film_title}"
    response = requests.get(search_url)
    search_results = response.json()["results"]

    if search_results:
        movie_data = search_results[0]
        movie_title = movie_data["title"]
        rental_database.movies[movie_title] = {
            "release_date": movie_data["release_date"],
            "overview": movie_data["overview"],
            "is_rented": False
        }

        print(f"Znaleziono film: {movie_title}")
        return render_template('index.html', result=f"Znaleziono film: {movie_title}", movie_title=movie_title)
    else:
        return render_template('index.html', result="Nie znaleziono filmu o podanym tytule.")


if __name__ == '__main__':
    app.run(debug=True)

