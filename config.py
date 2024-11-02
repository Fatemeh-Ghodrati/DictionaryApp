import os

class Config:
    API_KEY = os.getenv("API_KEY", "VENRbDgPZZ9h48RKhf7JQg==GHyAUNRAuMQo6hz7")
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    CACHE_TIMEOUT = os.getenv("CACHE_TIMEOUT", 300)
    PORT = os.getenv("PORT", 8020)
