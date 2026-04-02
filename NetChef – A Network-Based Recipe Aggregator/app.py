from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
import time
import pandas as pd
import json
import redis
from redis.exceptions import ConnectionError as RedisConnectionError

load_dotenv()

app = Flask(__name__)

SPOONACULAR_API = {
    "url": "https://api.spoonacular.com/recipes/complexSearch",
    "key": os.getenv("SPOONACULAR_KEY")
}

# Initialize Redis client with error handling
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        socket_connect_timeout=3,  # 3 seconds timeout
        socket_timeout=3
    )
    # Test the connection
    redis_client.ping()
except RedisConnectionError:
    redis_client = None
    print("Warning: Could not connect to Redis. Caching will be disabled.")


def get_cached_recipes(ingredient: str) -> dict | None:
    if not redis_client:
        return None

    cache_key = f"recipes:{ingredient}"
    try:
        cached = redis_client.get(cache_key)
        if cached is not None:
            return json.loads(cached.decode('utf-8'))
    except RedisConnectionError:
        return None
    return None


def set_cache(ingredient: str, data: dict, ttl: int = 3600) -> None:
    if not redis_client:
        return

    cache_key = f"recipes:{ingredient}"
    try:
        redis_client.setex(cache_key, ttl, json.dumps(data))
    except RedisConnectionError:
        pass  # Silently fail if Redis is unavailable


@app.route('/recipes', methods=['GET'])
def get_recipes():
    ingredient = request.args.get('ingredient')
    if not ingredient:
        return jsonify({"error": "Ingredient parameter is required"}), 400

    # Try cache first if Redis is available
    cached = get_cached_recipes(ingredient)
    if cached:
        return jsonify({"recipes": cached, "source": "cache"})

    recipes = []
    timings = {}

    start_time = time.time()
    params = {
        "query": ingredient,
        "apiKey": SPOONACULAR_API["key"]
    }

    try:
        response = requests.get(SPOONACULAR_API["url"], params=params)
        response.raise_for_status()
        data = response.json()
        recipes.extend(data.get('results', []))
        timings["spoonacular"] = str(time.time() - start_time)
    except requests.exceptions.RequestException as err:
        timings["spoonacular"] = f"Error: {str(err)}"

    # Cache the results if Redis is available
    set_cache(ingredient, recipes)

    # Save timings
    pd.DataFrame.from_dict(timings, orient='index', columns=['Time']).to_csv('timings.csv')
    return jsonify({"recipes": recipes, "timings": timings})


if __name__ == '__main__':
    try:
        app.run(debug=True, port=5050, use_reloader=False)
    except OSError as os_err:
        print(f"Error: {os_err}")