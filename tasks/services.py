import urllib.request
import json


def get_motivational_quote():
    url = "https://api.example.com/quotes/random"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data["quote"]
