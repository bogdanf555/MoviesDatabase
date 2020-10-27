import requests
import re
from bs4 import BeautifulSoup

# the IMDb website to scrape the information needed
url = "https://www.imdb.com/title/"

# sql insert statements for tables
insert_into_genres = "INSERT INTO genres (name) VALUES ('{}');"
insert_into_directors = "INSERT INTO directors (director_id, name) VALUES ('{}', '{}');"
insert_into_genres_of_movies = \
    "INSERT INTO genres_of_movies (movie_id, genre_id) VALUES ('{}', '{}');"
insert_into_directors_of_movies = \
    "INSERT INTO directors_of_movies (movie_id, director_id) VALUES ('{}', '{}');"

duplicate_genres_of_movies = \
    "SELECT 1 FROM genres_of_movies\
     WHERE movie_id='{}' and genre_id='{}';"

duplicate_directors_of_movies = \
    "SELECT 1 FROM directors_of_movies\
     WHERE movie_id='{}' and director_id='{}';"


def getDirectorsList(directors_elements):
    """
    :param directors_elements: a list of element objects containing the link html tags
        with the directors ids in the href attribute and the full name as text
    :returns directors_list: a list of dictionaries containing the id and the
        name of a director
    """
    directors_list = []

    for elem in directors_elements:
        try:
            director_id = re.search('/name/(.+?)/', elem['href']).group(1)
            name = elem.text.replace("'", "''")

            director = {"id": director_id, "name": name}
            directors_list.append(director)
        except:
            pass

    return directors_list


def getGenresList(genres):
    """
    :param genres: a list of element objects containing the link html tags with
        the genres name as their text
    :return genre_list: list of all the genres present in the list of elements
        parsed as strings
    """

    genre_list = []

    for i in range(len(genres) - 1):
        genre_list.append(genres[i].text.replace("'", "''"))

    return genre_list


def scrapeGenresAndDirectors(movie_ids_list):
    """
        Scrapes from IMDB the genres and directors of each movie in the ids list.

    :param movie_ids_list: a list of strings containing ids of movies
    :return movie_list: a list of dictionaries containing the id of movie (string),
            a list of its genres (strings), a list of directors dictionaries
    """
    movie_list = []

    for movie_id in movie_ids_list:

        response = requests.get(url + movie_id)
        movie_page = BeautifulSoup(response.text, "html.parser")

        genres = movie_page.find("div", {"class": "subtext"}).findAll("a")
        directors_elements = movie_page.find("div", {"credit_summary_item"}).findAll("a", href=True)

        genre_list = getGenresList(genres)
        directors_list = getDirectorsList(directors_elements)

        movie_dict = {"movie_id": movie_id, "genres": genre_list, "directors": directors_list}

        movie_list.append(movie_dict)

    return movie_list
