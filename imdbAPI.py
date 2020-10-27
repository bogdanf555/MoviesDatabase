import requests
import json
import sqlite3 as sql
import re

# url of request to the imdb api
url = "https://imdb-internet-movie-database-unofficial.p.rapidapi.com/film/"

# headers to pass to the request
headers = {
    'x-rapidapi-host': "imdb-internet-movie-database-unofficial.p.rapidapi.com",
    'x-rapidapi-key': "6fae38f5d6msh5243996cd2a9653p122166jsnc11c3ed7fb29"
}

# queries to populate the movies, actors and actors_in_movies tables
insertIntoMovies = \
    "INSERT INTO movies (movie_id, title, release_year, duration, imdb_rating) VALUES ('{}', '{}', {}, '{}', {});"

insertIntoActors = "INSERT INTO actors (actor_id, name) VALUES ('{}', '{}');"

insertIntoActorsInMovies = \
    "INSERT INTO actors_in_movies (movie_id, actor_id, character) VALUES ('{}', '{}', '{}');"

# select queries
duplicate_actors_in_movies = \
    "SELECT 1 FROM actors_in_movies\
     WHERE movie_id='{}' and actor_id='{}' and character='{}';"


def getTopRatedIds():
    """
    :return list_movie_id: list of strings (ids of top 250 top rated movies on imdb)
    """

    with open("top_rated_movies.txt") as f:
        top_rated_list = json.load(f)

    return [re.search('/title/(.+?)/', i['id']).group(1) for i in top_rated_list]


def createProperMovieDictionary(raw_dict):
    """
    Takes the dictionary provided by the request (full of strings)
    and formats it where some variables need to have other types (e.g int, float)
    also escapes all the single quotes characters in strings

    :param raw_dict: the raw dictionary with the movie information provided by the api
    :return proper_dict: a dictionary with the proper types to input in the database
                         containing id, title, year, length, rating and the cast
                         (a dictionary of actors in movies)
    """

    try:
        year = int(raw_dict['year'])
    except ValueError:
        year = 0

    try:
        rating = float(raw_dict['rating'])
    except ValueError:
        rating = 0.0

    proper_dict = {
        'id': raw_dict['id'],
        'title': raw_dict['title'].replace(u'\xa0', u'').replace("'", "''"),
        'year': year,
        'length': raw_dict['length'],
        'rating': rating,
        'cast': raw_dict['cast']
    }

    for actor in proper_dict['cast']:
        actor['actor'] = actor['actor'].replace("'", "''")
        actor['character'] = actor['character'].replace("'", "''")

    return proper_dict


def getInfoMovies(ids_list):
    """
    :param ids_list: list of strings representing a collection of movie ids

    :return movies: list of dictionaries representing information about
        every movie (id, title, year, rating , length, cast)
    """

    movies = []

    for movie_id in ids_list:
        response = requests.request("GET", url + movie_id, headers=headers)
        movie_dictionary_raw = json.loads(response.text)
        movie_dictionary = createProperMovieDictionary(movie_dictionary_raw)
        movies.append(movie_dictionary)

    return movies


def connectToDB():
    """
    :returns connection: an connection object to the movie database, in case of exception
        returns None
    """

    try:
        return sql.connect("Movie_Database")
    except sql.DatabaseError:
        return None


def getCursor(connection):
    """
    :param connection: a connection to the movie database
    :returns cursor: a cursor for the database, in case of exception returns None
    """

    try:
        return connection.cursor()
    except sql.DatabaseError:
        return None
