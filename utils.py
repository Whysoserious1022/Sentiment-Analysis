"""
Utility functions for text processing and analysis
"""

import re
import json
from datetime import datetime
from typing import List, Dict, Any


def clean_text(text: str) -> str:
    """Clean and preprocess text for analysis"""
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    # Remove excessive punctuation
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    
    return text.strip()


def extract_aspects(text: str) -> List[str]:
    """
    Extract key aspects/entities from text for aspect-based sentiment analysis
    Simple implementation using common patterns
    """
    aspects = []
    
    # Common aspect patterns (nouns typically)
    words = text.lower().split()
    
    # Common subjects in reviews
    common_aspects = [
        'food', 'service', 'staff', 'price', 'quality', 'location',
        'product', 'delivery', 'packaging', 'support', 'experience',
        'design', 'performance', 'battery', 'camera', 'screen',
        'sound', 'value', 'customer service', 'ambiance', 'menu'
    ]
    
    for aspect in common_aspects:
        if aspect in text.lower():
            aspects.append(aspect)
    
    return aspects if aspects else ['overall']


def format_sentiment_result(label: str, score: float, all_scores: Dict[str, float]) -> Dict[str, Any]:
    """Format sentiment analysis results"""
    return {
        'label': label.lower(),
        'confidence': round(score, 4),
        'all_scores': {k.lower(): round(v, 4) for k, v in all_scores.items()},
        'timestamp': datetime.now().isoformat()
    }


def format_emotion_result(emotions: Dict[str, float]) -> Dict[str, Any]:
    """Format emotion detection results"""
    # Get top emotion
    top_emotion = max(emotions.items(), key=lambda x: x[1])
    
    return {
        'primary_emotion': top_emotion[0],
        'confidence': round(top_emotion[1], 4),
        'all_emotions': {k: round(v, 4) for k, v in emotions.items()},
        'timestamp': datetime.now().isoformat()
    }


def format_aspect_result(aspects_sentiments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Format aspect-based sentiment results"""
    return {
        'aspects': aspects_sentiments,
        'aspect_count': len(aspects_sentiments),
        'timestamp': datetime.now().isoformat()
    }


def calculate_overall_sentiment(sentiments: List[str]) -> str:
    """Calculate overall sentiment from multiple sentiments"""
    if not sentiments:
        return 'neutral'
    
    counts = {
        'positive': sentiments.count('positive'),
        'negative': sentiments.count('negative'),
        'neutral': sentiments.count('neutral')
    }
    
    return max(counts.items(), key=lambda x: x[1])[0]


def export_to_json(data: Any, filename: str = None) -> str:
    """Export data to JSON format"""
    if filename:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return filename
    return json.dumps(data, indent=2)


def validate_text_input(text: str, max_length: int = 5000) -> tuple[bool, str]:
    """Validate text input"""
    if not text or not text.strip():
        return False, "Text cannot be empty"
    
    if len(text) > max_length:
        return False, f"Text exceeds maximum length of {max_length} characters"
    
    return True, "Valid"


def get_sentiment_color(sentiment: str) -> str:
    """Get color code for sentiment"""
    colors = {
        'positive': '#10b981',
        'negative': '#ef4444',
        'neutral': '#6b7280'
    }
    return colors.get(sentiment.lower(), '#6b7280')


def get_emotion_emoji(emotion: str) -> str:
    """Get emoji for emotion"""
    emojis = {
        'joy': '😊',
        'sadness': '😢',
        'anger': '😠',
        'fear': '😨',
        'surprise': '😮',
        'disgust': '🤢',
        'love': '❤️',
        'neutral': '😐'
    }
    return emojis.get(emotion.lower(), '😐')
