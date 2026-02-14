// ============================================
// SENTIMENT ANALYSIS - CLIENT-SIDE LOGIC
// ============================================

// State management
let currentMode = 'sentiment';
let sentimentChart = null;
let emotionChart = null;

// Sample texts for demo
const sampleTexts = {
    sentiment: "I absolutely love this product! The quality is amazing and the customer service was excellent. Highly recommend!",
    emotion: "I'm so excited about this opportunity! It's a dream come true and I couldn't be happier.",
    aspect: "The food was absolutely delicious and fresh, but the service was quite slow. The ambiance was nice though."
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadHistory();
});

// Event Listeners
function initializeEventListeners() {
    // Mode selector
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => switchMode(btn.dataset.mode));
    });

    // Text input
    const textInput = document.getElementById('textInput');
    textInput.addEventListener('input', updateCharCounter);

    // Buttons
    document.getElementById('analyzeBtn').addEventListener('click', analyzeText);
    document.getElementById('clearBtn').addEventListener('click', clearInput);
    document.getElementById('sampleBtn').addEventListener('click', loadSample);
    document.getElementById('batchAnalyzeBtn').addEventListener('click', batchAnalyze);
    document.getElementById('clearHistoryBtn').addEventListener('click', clearHistory);

    // Enter to submit
    textInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            analyzeText();
        }
    });
}

// Mode switching
function switchMode(mode) {
    currentMode = mode;

    // Update button states
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    // Hide all result cards
    document.getElementById('sentimentResults').style.display = 'none';
    document.getElementById('emotionResults').style.display = 'none';
    document.getElementById('aspectResults').style.display = 'none';
}

// Update character counter
function updateCharCounter() {
    const input = document.getElementById('textInput');
    const counter = document.getElementById('charCounter');
    counter.textContent = `${input.value.length} / 5000`;
}

// Clear input
function clearInput() {
    document.getElementById('textInput').value = '';
    updateCharCounter();
    document.getElementById('resultsSection').style.display = 'none';
}

// Load sample text
function loadSample() {
    document.getElementById('textInput').value = sampleTexts[currentMode];
    updateCharCounter();
}

// Analyze text
async function analyzeText() {
    const text = document.getElementById('textInput').value.trim();

    if (!text) {
        alert('Please enter some text to analyze');
        return;
    }

    // Show loading
    document.getElementById('loadingState').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';

    try {
        let endpoint, resultHandler;

        switch (currentMode) {
            case 'sentiment':
                endpoint = '/api/analyze';
                resultHandler = displaySentimentResults;
                break;
            case 'emotion':
                endpoint = '/api/emotion';
                resultHandler = displayEmotionResults;
                break;
            case 'aspect':
                endpoint = '/api/aspect';
                resultHandler = displayAspectResults;
                break;
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        // Display results
        resultHandler(data);

        // Reload history
        loadHistory();

    } catch (error) {
        alert('Analysis failed: ' + error.message);
    } finally {
        document.getElementById('loadingState').style.display = 'none';
    }
}

// Display sentiment results
function displaySentimentResults(data) {
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('sentimentResults').style.display = 'block';

    // Update label
    const label = data.label;
    const confidence = data.confidence;

    // Emoji mapping
    const emojiMap = {
        positive: '😊',
        negative: '😞',
        neutral: '😐'
    };

    document.getElementById('sentimentEmoji').textContent = emojiMap[label] || '😐';
    document.getElementById('sentimentText').textContent = label.charAt(0).toUpperCase() + label.slice(1);

    // Color coding
    const colorMap = {
        positive: '#10b981',
        negative: '#ef4444',
        neutral: '#6b7280'
    };

    const sentimentLabel = document.querySelector('.sentiment-label');
    sentimentLabel.style.borderLeft = `6px solid ${colorMap[label]}`;

    // Confidence bar
    const confidenceFill = document.getElementById('confidenceFill');
    const confidenceValue = document.getElementById('confidenceValue');

    confidenceFill.style.width = (confidence * 100) + '%';
    confidenceFill.style.background = `linear-gradient(90deg, ${colorMap[label]}, ${colorMap[label]}dd)`;
    confidenceValue.textContent = (confidence * 100).toFixed(1) + '%';

    // Create chart
    createSentimentChart(data.all_scores);
}

// Create sentiment chart
function createSentimentChart(scores) {
    const ctx = document.getElementById('sentimentChart');

    if (sentimentChart) {
        sentimentChart.destroy();
    }

    const labels = Object.keys(scores).map(k => k.charAt(0).toUpperCase() + k.slice(1));
    const values = Object.values(scores).map(v => (v * 100).toFixed(1));

    const colors = {
        'Positive': '#10b981',
        'Negative': '#ef4444',
        'Neutral': '#6b7280'
    };

    sentimentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Confidence (%)',
                data: values,
                backgroundColor: labels.map(l => colors[l] || '#667eea'),
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                x: {
                    ticks: { color: '#94a3b8' },
                    grid: { display: false }
                }
            }
        }
    });
}

// Display emotion results
function displayEmotionResults(data) {
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('emotionResults').style.display = 'block';

    const emotion = data.primary_emotion;
    const confidence = data.confidence;

    // Emoji mapping
    const emojiMap = {
        joy: '😊',
        sadness: '😢',
        anger: '😠',
        fear: '😨',
        surprise: '😮',
        disgust: '🤢',
        love: '❤️',
        neutral: '😐'
    };

    document.getElementById('emotionEmoji').textContent = emojiMap[emotion] || '😐';
    document.getElementById('emotionText').textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
    document.getElementById('emotionConfidence').textContent = (confidence * 100).toFixed(1) + '%';

    // Create emotion chart
    createEmotionChart(data.all_emotions);
}

// Create emotion chart
function createEmotionChart(emotions) {
    const ctx = document.getElementById('emotionChart');

    if (emotionChart) {
        emotionChart.destroy();
    }

    const labels = Object.keys(emotions).map(k => k.charAt(0).toUpperCase() + k.slice(1));
    const values = Object.values(emotions).map(v => (v * 100).toFixed(1));

    emotionChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Emotion Scores',
                data: values,
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                borderColor: '#667eea',
                borderWidth: 2,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: '#94a3b8',
                        backdropColor: 'transparent'
                    },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    pointLabels: { color: '#cbd5e1', font: { size: 12 } }
                }
            }
        }
    });
}

// Display aspect results
function displayAspectResults(data) {
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('aspectResults').style.display = 'block';

    const aspectList = document.getElementById('aspectList');
    aspectList.innerHTML = '';

    if (data.aspects && data.aspects.length > 0) {
        data.aspects.forEach(aspect => {
            const item = document.createElement('div');
            item.className = `aspect-item ${aspect.sentiment}`;

            item.innerHTML = `
                <span class="aspect-name">${aspect.aspect}</span>
                <div class="aspect-sentiment">
                    <span class="aspect-badge ${aspect.sentiment}">
                        ${aspect.sentiment}
                    </span>
                    <span>${(aspect.confidence * 100).toFixed(1)}%</span>
                </div>
            `;

            aspectList.appendChild(item);
        });
    } else {
        aspectList.innerHTML = '<p class="empty-state">No aspects detected</p>';
    }
}

// Batch analyze
async function batchAnalyze() {
    const batchInput = document.getElementById('batchInput').value.trim();

    if (!batchInput) {
        alert('Please enter texts for batch processing');
        return;
    }

    const texts = batchInput.split('\n').filter(t => t.trim());

    if (texts.length === 0) {
        alert('No valid texts found');
        return;
    }

    // Show loading
    const btn = document.getElementById('batchAnalyzeBtn');
    btn.disabled = true;
    btn.innerHTML = '<span>Processing...</span>';

    try {
        const response = await fetch('/api/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ texts, mode: currentMode })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        displayBatchResults(data.results);

    } catch (error) {
        alert('Batch analysis failed: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-text">Analyze Batch</span><span class="btn-icon">🚀</span>';
    }
}

// Display batch results
function displayBatchResults(results) {
    const container = document.getElementById('batchResults');
    container.innerHTML = '';

    results.forEach((result, index) => {
        const item = document.createElement('div');

        let sentiment = 'neutral';
        let text = `Text ${index + 1}`;

        if (result.label) {
            sentiment = result.label;
            text = `${result.label.charAt(0).toUpperCase() + result.label.slice(1)} (${(result.confidence * 100).toFixed(1)}%)`;
        } else if (result.primary_emotion) {
            sentiment = 'neutral';
            text = `${result.primary_emotion.charAt(0).toUpperCase() + result.primary_emotion.slice(1)} (${(result.confidence * 100).toFixed(1)}%)`;
        }

        item.className = `batch-result-item ${sentiment}`;
        item.innerHTML = `
            <div class="batch-text">Text ${index + 1}</div>
            <div class="batch-sentiment">${text}</div>
        `;

        container.appendChild(item);
    });
}

// Load history
async function loadHistory() {
    try {
        const response = await fetch('/api/history?limit=10');
        const data = await response.json();

        const historyList = document.getElementById('historyList');

        if (data.history && data.history.length > 0) {
            historyList.innerHTML = '';

            data.history.reverse().forEach(item => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';

                const timestamp = new Date(item.timestamp).toLocaleString();

                historyItem.innerHTML = `
                    <div class="history-meta">
                        <span>${item.type}</span>
                        <span>${timestamp}</span>
                    </div>
                    <div class="history-text">${item.text}</div>
                `;

                historyItem.addEventListener('click', () => {
                    document.getElementById('textInput').value = item.text;
                    updateCharCounter();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                });

                historyList.appendChild(historyItem);
            });
        } else {
            historyList.innerHTML = '<p class="empty-state">No analysis history yet. Start analyzing!</p>';
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Clear history
async function clearHistory() {
    if (!confirm('Are you sure you want to clear all history?')) {
        return;
    }

    try {
        await fetch('/api/clear-history', { method: 'POST' });
        loadHistory();
    } catch (error) {
        alert('Failed to clear history: ' + error.message);
    }
}
