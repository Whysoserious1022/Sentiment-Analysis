"""
ML Models for Sentiment and Emotion Analysis
Using pre-trained transformers from Hugging Face
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import numpy as np
from typing import Dict, List, Tuple
import config
import utils


class SentimentAnalyzer:
    """Sentiment Analysis using RoBERTa model"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
    def _load_model(self):
        """Lazy load the sentiment model"""
        if self.pipeline is None:
            print(f"Loading sentiment model: {config.SENTIMENT_MODEL}")
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=config.SENTIMENT_MODEL,
                tokenizer=config.SENTIMENT_MODEL,
                device=0 if torch.cuda.is_available() else -1
            )
            print("Sentiment model loaded successfully!")
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        Returns: dict with label, confidence, and all scores
        """
        # Validate input
        is_valid, message = utils.validate_text_input(text, config.MAX_TEXT_LENGTH)
        if not is_valid:
            return {'error': message}
        
        # Clean text
        cleaned_text = utils.clean_text(text)
        
        # Load model if not loaded
        self._load_model()
        
        # Get prediction
        try:
            result = self.pipeline(cleaned_text, top_k=None)
            
            # Cardiff NLP model uses LABEL_0, LABEL_1, LABEL_2
            # Map to human-readable labels
            label_mapping = {
                'LABEL_0': 'negative',
                'LABEL_1': 'neutral',
                'LABEL_2': 'positive',
                # Also support already-mapped labels
                'negative': 'negative',
                'neutral': 'neutral',
                'positive': 'positive'
            }
            
            # Pipeline returns a list of list: [[{label, score}, ...]]
            # Get the first (and only) result for single text input
            predictions = result[0] if isinstance(result[0], list) else result
            
            # Parse results and map labels
            all_scores = {}
            for item in predictions:
                mapped_label = label_mapping.get(item['label'], item['label'].lower())
                all_scores[mapped_label] = item['score']
            
            top_result = max(predictions, key=lambda x: x['score'])
            top_label = label_mapping.get(top_result['label'], top_result['label'].lower())
            
            return utils.format_sentiment_result(
                label=top_label,
                score=top_result['score'],
                all_scores=all_scores
            )
        except Exception as e:
            import traceback
            traceback.print_exc()  # Debug: print full traceback
            return {'error': f"Analysis failed: {str(e)}"}
    
    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple texts"""
        return [self.analyze_sentiment(text) for text in texts]


class EmotionAnalyzer:
    """Emotion Detection using DistilRoBERTa model"""
    
    def __init__(self):
        self.pipeline = None
        
    def _load_model(self):
        """Lazy load the emotion model"""
        if self.pipeline is None:
            print(f"Loading emotion model: {config.EMOTION_MODEL}")
            self.pipeline = pipeline(
                "text-classification",
                model=config.EMOTION_MODEL,
                tokenizer=config.EMOTION_MODEL,
                top_k=None,
                device=0 if torch.cuda.is_available() else -1
            )
            print("Emotion model loaded successfully!")
    
    def analyze_emotion(self, text: str) -> Dict:
        """
        Detect emotions in text
        Returns: dict with primary emotion and all emotion scores
        """
        # Validate input
        is_valid, message = utils.validate_text_input(text, config.MAX_TEXT_LENGTH)
        if not is_valid:
            return {'error': message}
        
        # Clean text
        cleaned_text = utils.clean_text(text)
        
        # Load model if not loaded
        self._load_model()
        
        # Get prediction
        try:
            result = self.pipeline(cleaned_text)
            
            # Parse results
            emotions = {item['label']: item['score'] for item in result[0]}
            
            return utils.format_emotion_result(emotions)
        except Exception as e:
            return {'error': f"Emotion analysis failed: {str(e)}"}


class AspectBasedAnalyzer:
    """Aspect-based sentiment analysis"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        
    def analyze_aspects(self, text: str) -> Dict:
        """
        Extract aspects and analyze sentiment for each
        Returns: dict with aspect-sentiment pairs
        """
        # Validate input
        is_valid, message = utils.validate_text_input(text, config.MAX_TEXT_LENGTH)
        if not is_valid:
            return {'error': message}
        
        # Extract aspects
        aspects = utils.extract_aspects(text)
        
        # Analyze overall sentiment for context
        overall_sentiment = self.sentiment_analyzer.analyze_sentiment(text)
        
        # For each aspect, try to find relevant sentences
        aspect_sentiments = []
        
        sentences = text.split('.')
        
        for aspect in aspects:
            # Find sentences mentioning this aspect
            relevant_sentences = [s for s in sentences if aspect in s.lower()]
            
            if relevant_sentences:
                # Analyze sentiment of these sentences
                aspect_text = '. '.join(relevant_sentences)
                sentiment = self.sentiment_analyzer.analyze_sentiment(aspect_text)
            else:
                # Use overall sentiment
                sentiment = overall_sentiment
            
            aspect_sentiments.append({
                'aspect': aspect,
                'sentiment': sentiment.get('label', 'neutral'),
                'confidence': sentiment.get('confidence', 0.0),
                'emoji': utils.get_sentiment_color(sentiment.get('label', 'neutral'))
            })
        
        return utils.format_aspect_result(aspect_sentiments)


# Global instances (lazy loaded)
sentiment_analyzer = SentimentAnalyzer()
emotion_analyzer = EmotionAnalyzer()
aspect_analyzer = AspectBasedAnalyzer()
