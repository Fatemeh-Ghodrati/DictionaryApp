from flask import Flask, jsonify, request
import requests
import redis
import time
from config import Config
from prometheus_client import Counter, Histogram, generate_latest, CollectorRegistry

app = Flask(__name__)
app.config.from_object(Config)

r = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], decode_responses=True)

registry = CollectorRegistry()

api_requests = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['endpoint']
)

redis_requests = Counter(
    'redis_requests_total',
    'Total number of requests read from Redis'
)

successful_requests = Counter(
    'successful_requests_total',
    'Total number of successful requests'
)

failed_requests = Counter(
    'failed_requests_total',
    'Total number of failed requests'
)

api_latency = Histogram(
    'api_latency_seconds',
    'API latency in seconds',
    ['endpoint']
)

@app.route('/word/<string:word>', methods=['GET'])
def get_word_meaning(word):
    start_time = time.time()
    endpoint = '/word'
    
    api_requests.inc({'endpoint': endpoint})
    
    cached_result = r.get(word)
    if cached_result:
        redis_requests.inc()
        return jsonify({"result": cached_result, "source": "redis"}), 200

    api_url = f'https://api.api-ninjas.com/v1/dictionary?word={word}'
    response = requests.get(api_url, headers={'X-Api-Key': app.config['API_KEY']})
    
    latency = time.time() - start_time
    api_latency.labels(endpoint=endpoint).observe(latency)

    if response.status_code == requests.codes.ok:
        meaning = response.json().get('definition')
        if meaning:
            r.setex(word, app.config['CACHE_TIMEOUT'], meaning)
            successful_requests.inc()
            return jsonify({"meaning": meaning})
        else:
            failed_requests.inc() 
            return jsonify({"error": "Meaning not found in the response"}), 404
    else:
        failed_requests.inc() 
        return jsonify({"error": response.status_code, "message": response.text}), response.status_code

@app.route('/random_words', methods=['GET'])
def get_random_word():
    start_time = time.time()
    endpoint = '/random_words'
    
    api_requests.inc({'endpoint': endpoint})
    
    api_url = 'https://api.api-ninjas.com/v1/randomword'
    response = requests.get(api_url, headers={'X-Api-Key': app.config['API_KEY']})
    
    latency = time.time() - start_time
    api_latency.labels(endpoint=endpoint).observe(latency)

    if response.status_code == requests.codes.ok:
        random_word_data = response.json()
        successful_requests.inc()
        return jsonify(random_word_data), 200
    else:
        failed_requests.inc()
        return jsonify({"error": response.status_code, "message": response.text}), response.status_code

def metrics():
    return generate_latest(registry), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'])
