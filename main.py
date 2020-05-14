import json
import requests
from geopy import distance
from pprint import pprint
import folium
import os
from flask import Flask


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon

    
def get_distance_to_bar(bar):
    return bar["distance"]

def show_map_with_closest_bars():
    with open('index.html') as file:
      return file.read()
  

def main():
    with open("bars.json", "r", encoding="CP1251") as my_file:
        bars_json = my_file.read()

    bars = json.loads(bars_json)
    apikey = os.getenv("APIKEY")
    your_location = input("Где вы находитесь?")
    coords_of_you = fetch_coordinates(apikey, your_location)
    all_bars = []
    for bar in bars:
        name = bar['Name']
        longitude = bar['geoData']['coordinates'][0]
        latitude = bar['geoData']['coordinates'][1]
        bar_location = []
        bar_location.append(latitude)
        bar_location.append(longitude)
        bar_for_dict = {
          "title": bar['Name'],
          "longitude": bar['geoData']['coordinates'][0],
          "latitude": bar['geoData']['coordinates'][1],
          "distance": distance.distance(coords_of_you, bar_location).km
        }
        all_bars.append(bar_for_dict)

    closest_bars_amount = 5
    sorted_bars = sorted(all_bars, key=get_distance_to_bar)
    closest_bars = sorted_bars[:closest_bars_amount]

    map_with_bars = folium.Map(location=coords_of_you, zoom_start=12)
    tooltip = 'Нажми на меня!'

    for bar_number, bar in enumerate(closest_bars):
        folium.Marker([closest_bars[bar_number]['latitude'], closest_bars[bar_number]['longitude']], popup=closest_bars[bar_number]['title'], tooltip=tooltip).add_to(map_with_bars)

    map_with_bars.save('index.html')

    app = Flask(__name__)
    app.add_url_rule('/', 'closest bars', show_map_with_closest_bars)
    app.run('0.0.0.0')

if __name__ == '__main__':
    main()