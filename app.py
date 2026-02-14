"""
Flask Application for Sentiment Analysis
Main entry point for the web application
"""

from flask import Flask, render_template, request, jsonify
import config
from models import sentiment_analyzer, emotion_analyzer, aspect_analyzer
import utils
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Store analysis history (in-memory, could use DB for production)
analysis_history = []


@app.route('/')
def index():
    """Render main application page"""
    return render_template('index.html', config=config)


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze sentiment of text
    Expects JSON: {"text": "your text here"}
    Returns: sentiment analysis result
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Perform sentiment analysis
        result = sentiment_analyzer.analyze_sentiment(text)
        
        # Debug: print the result
        print(f"Sentiment analysis result: {result}")
        
        if 'error' in result:
            print(f"Error in result: {result['error']}")
            return jsonify(result), 400
        
        # Add to history
        history_entry = {
            'id': len(analysis_history) + 1,
            'text': text[:100] + '...' if len(text) > 100 else text,
            'type': 'sentiment',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        analysis_history.append(history_entry)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Exception in /api/analyze: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/emotion', methods=['POST'])
def analyze_emotion():
    """
    Analyze emotions in text
    Expects JSON: {"text": "your text here"}
    Returns: emotion analysis result
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Perform emotion analysis
        result = emotion_analyzer.analyze_emotion(text)
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Add to history
        history_entry = {
            'id': len(analysis_history) + 1,
            'text': text[:100] + '...' if len(text) > 100 else text,
            'type': 'emotion',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        analysis_history.append(history_entry)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/aspect', methods=['POST'])
def analyze_aspect():
    """
    Perform aspect-based sentiment analysis
    Expects JSON: {"text": "your text here"}
    Returns: aspect-based analysis result
    """
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Perform aspect-based analysis
        result = aspect_analyzer.analyze_aspects(text)
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Add to history
        history_entry = {
            'id': len(analysis_history) + 1,
            'text': text[:100] + '...' if len(text) > 100 else text,
            'type': 'aspect',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        analysis_history.append(history_entry)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch', methods=['POST'])
def batch_analyze():
    """
    Batch process multiple texts
    Expects JSON: {"texts": ["text1", "text2", ...], "mode": "sentiment|emotion|aspect"}
    Returns: list of results
    """
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        mode = data.get('mode', 'sentiment')
        
        if not texts or not isinstance(texts, list):
            return jsonify({'error': 'Invalid texts array'}), 400
        
        if len(texts) > config.BATCH_SIZE_LIMIT:
            return jsonify({'error': f'Batch size exceeds limit of {config.BATCH_SIZE_LIMIT}'}), 400
        
        # Process based on mode
        results = []
        for text in texts:
            if mode == 'sentiment':
                result = sentiment_analyzer.analyze_sentiment(text)
            elif mode == 'emotion':
                result = emotion_analyzer.analyze_emotion(text)
            elif mode == 'aspect':
                result = aspect_analyzer.analyze_aspects(text)
            else:
                result = {'error': 'Invalid mode'}
            
            results.append(result)
        
        return jsonify({
            'results': results,
            'count': len(results),
            'mode': mode
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get analysis history"""
    limit = request.args.get('limit', 20, type=int)
    return jsonify({
        'history': analysis_history[-limit:],
        'total': len(analysis_history)
    })


@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear analysis history"""
    global analysis_history
    analysis_history = []
    return jsonify({'message': 'History cleared'})


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models': {
            'sentiment': config.SENTIMENT_MODEL,
            'emotion': config.EMOTION_MODEL
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🎭 SENTIMENT ANALYSIS APPLICATION")
    print("=" * 60)
    print(f"Server starting on http://{config.HOST}:{config.PORT}")
    print(f"Sentiment Model: {config.SENTIMENT_MODEL}")
    print(f"Emotion Model: {config.EMOTION_MODEL}")
    print("=" * 60)
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
