# Databricks notebook source
import requests # is already in the databricks python environment
import json
import datetime

url = "https://pokeapi.co/api/v2/pokemon?limit=2000"

response = requests.get(url)
data = response.json()

data_save = data['results']

now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
path = f"/Volumes/raw/pokemon/pokemon_raw/pokemons_list/{now}.json"
# this is possible because we already have the Volumes mounted
# it wouldn't be possible if when using os.listdir() we haven't find the Volumes folder

with open(path, 'w') as open_file:
    json.dump(data_save, open_file)
