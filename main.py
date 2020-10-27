import imdbAPI
import collectGenresAndDirectors as cgd
from datetime import datetime
from sqlite3 import IntegrityError

if __name__ == '__main__':

    # connect to database and check connection
    connection = imdbAPI.connectToDB()
    cursor = imdbAPI.getCursor(connection)

    if connection is None or cursor is None:
        print("Connection to the database failed!")
        exit()

    # get the list of top 250 imdb top rated movies
    top_rated_ids = imdbAPI.getTopRatedIds()

    # to test running time for curiosity :))
    print("scrape start: ", datetime.now().strftime("%H:%M:%S"))

    # list of dictionaries containing the information about the genres
    # and directors of movies
    genres_and_directors_in_movies = cgd.scrapeGenresAndDirectors(top_rated_ids)

    # list of dictionaries containing information about movies and actors that
    # play in them
    top_rated_movies = imdbAPI.getInfoMovies(top_rated_ids)

    print("scrape done: ", datetime.now().strftime("%H:%M:%S"))

    # load genres and directors
    for entity in genres_and_directors_in_movies:

        for genre in entity['genres']:
            # add genre in genres table
            try:
                cursor.execute(cgd.insert_into_genres.format(genre))
            except IntegrityError:
                # genre already added
                print(genre + ": FAILED")

            # link genre with the current movie in genres_of_movies table
            # if this row is not already in the table
            cursor.execute(cgd.duplicate_genres_of_movies.format(entity['movie_id'], genre))

            if not cursor.fetchall():
                cursor.execute(cgd.insert_into_genres_of_movies
                               .format(entity['movie_id'], genre))

        for director in entity['directors']:
            # add director to the directors table
            try:
                cursor.execute(cgd.insert_into_directors
                               .format(director['id'], director['name']))
            except IntegrityError:
                # director already added
                print(director['name'] + ": FAILED")

            # link director to the current movie in directors_in_movies table
            # if this row is not already in the table
            cursor.execute(cgd.duplicate_directors_of_movies
                           .format(entity['movie_id'], director['id']))

            if not cursor.fetchall():
                cursor.execute(cgd.insert_into_directors_of_movies
                            .format(entity['movie_id'], director['id']))

    for movie in top_rated_movies:
        # add movie
        try:
            # if title is empty it meas the api didn't find the movie
            if movie['title'] != '':
                cursor.execute(imdbAPI.insertIntoMovies
                               .format(movie['id'], movie['title'], movie['year'],
                                       movie['length'], movie['rating']))
        except IntegrityError:
            # title already added
            print(movie['title'], " MOVIE FAILED")

        # add actors and link them with the movies in actors_in_movies
        # if this row is not already in the table
        for actor in movie['cast']:
            # add actor
            try:
                cursor.execute(imdbAPI.insertIntoActors
                               .format(actor['actor_id'], actor['actor']))
            except IntegrityError:
                # actor already added
                print(actor['actor'], "ACTOR FAILED")

            # link actor with movie in table actors_in_movies
            # also add the character that the actor is playing in that movie
            try:
                cursor.execute(imdbAPI.duplicate_actors_in_movies
                               .format(movie['id'], actor['actor_id'], actor['character']))

                if not cursor.fetchall():
                    cursor.execute(imdbAPI.insertIntoActorsInMovies
                                   .format(movie['id'], actor['actor_id'], actor['character']))
            except IntegrityError:
                print(movie['title'])
                print(actor['character'])
                exit()

    connection.commit()
    cursor.close()
    connection.close()
