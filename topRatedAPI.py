import requests

url = "https://imdb8.p.rapidapi.com/title/get-top-rated-movies"

headers = {
    'x-rapidapi-host': "imdb8.p.rapidapi.com",
    'x-rapidapi-key': "6fae38f5d6msh5243996cd2a9653p122166jsnc11c3ed7fb29"
    }

response = requests.request("GET", url, headers=headers)

# write the list of dictionaries ("id": string, "chartRating": float)
with open("top_rated_movies.txt", "w") as f:
    f.write(response.text)