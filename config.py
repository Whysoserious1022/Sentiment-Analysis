"""
Configuration settings for Sentiment Analysis application
"""

# Model Configuration
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"

# Application Settings
DEBUG = True
HOST = "127.0.0.1"
PORT = 5000
MAX_TEXT_LENGTH = 5000
BATCH_SIZE_LIMIT = 100

# UI Theme Colors
THEME = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "positive": "#10b981",
    "negative": "#ef4444",
    "neutral": "#6b7280",
    "background": "#0f172a",
    "surface": "#1e293b",
}

# Cache Settings
ENABLE_MODEL_CACHE = True
CACHE_DIR = "./model_cache"

# Feature Flags
ENABLE_EMOTION_DETECTION = True
ENABLE_ASPECT_ANALYSIS = True
ENABLE_BATCH_PROCESSING = True
ENABLE_HISTORY = True
