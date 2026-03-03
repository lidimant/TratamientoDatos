from fastapi import FastAPI, Request 
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import googlemaps
import pandas as pd
import time
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name='static')
templates = Jinja2Templates(directory="templates")

API_KEY = os.getenv("GOOGLE_API_KEY")

gmaps = googlemaps.Client(key=API_KEY)


def get_restaurants():
    location = (-0.159268, -78.464914)
    radius = 1000
    place_type = 'restaurant'

    results_list = []
    MAX_REQUEST = 40
    request_count = 0

    response = gmaps.places_nearby(
        location = location,
        radius = radius,
        type = place_type
    )

    while response:
        for place in response["results"]:
            results_list.append({
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "rating": place.get("rating"),
            "users": place.get("user_ratings_total"),
            "lat": place["geometry"]["location"]["lat"],
            "lng": place["geometry"]["location"]["lng"]    
            })

            request_count += 1
            if request_count >= MAX_REQUEST:
                break

        if "next_page_token" in response and request_count < MAX_REQUEST:
            time.sleep(5)
            response = gmaps.places_nearby(
                page_token = response['next_page_token']
            )
        else:
            break

    return results_list

@app.get("/api/restaurants")
def restaurants_api():
    return get_restaurants()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
