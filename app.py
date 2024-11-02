from flask import Flask, jsonify, request
import requests
import redis
import time
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

r = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], decode_responses=True)

@app.route('/word/<string:word>', methods=['GET'])
def get_word_meaning(word):
    cached_result = r.get(word)
    if cached_result:
        return jsonify({"result": cached_result, "source": "redis"}), 200

    api_url = f'https://api.api-ninjas.com/v1/dictionary?word={word}'
    response = requests.get(api_url, headers={'X-Api-Key': app.config['API_KEY']})

    if response.status_code == requests.codes.ok:
        meaning = response.json().get('meaning')
        r.setex(word, app.config['CACHE_TIMEOUT'], meaning)
        return jsonify({"result": meaning, "source": "api-ninjas"}), 200
    else:
        return jsonify({"error": response.status_code, "message": response.text}), response.status_code

@app.route('/randomword', methods=['GET'])
def get_random_word():
    api_url = 'https://api.api-ninjas.com/v1/randomword'
    response = requests.get(api_url, headers={'X-Api-Key': app.config['API_KEY']})

    if response.status_code == requests.codes.ok:
        random_word_data = response.json()
        return jsonify(random_word_data), 200
    else:
        return jsonify({"error": response.status_code, "message": response.text}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'])
