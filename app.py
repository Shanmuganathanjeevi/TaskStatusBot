"""
TasksStatusBot Web Application
Flask backend for TasksStatusBot RAG system
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import traceback
import signal

# Import your existing modules
from document_processor import DocumentProcessor
from qa_engine import QAEngine

# ============================================================
# BASIC BOT APP SETUP
# ============================================================

# Global processor - load tasks once on startup
task_processor = None

# Initialize Model2Vec once on startup (not per request)
print("Loading embedding model...")
from model2vec import StaticModel
global embedding_model
embedding_model = StaticModel.from_pretrained("minishlab/potion-base-8M")
print("✓ Embedding model loaded")

def load_tasks():
    """Load tasks from CSV + TXT files on startup"""
    global task_processor
    
    tasks_folder = 'tasks'
    
    if not os.path.exists(tasks_folder):
        print(f"⚠️  Warning: {tasks_folder} folder not found")
        return False
    
    try:
        print("Loading tasks from 'tasks' folder...")
        task_processor = DocumentProcessor()
        task_processor.process_multiple_files(tasks_folder)
        print("✅ Tasks loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading tasks: {str(e)}")
        return False

# ============================================================
# CONFIGURATION
# ============================================================

app = Flask(__name__)
app.secret_key = 'documentai-secret-key-change-in-prod'  # For sessions
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf'}

# In-memory storage for demo (in production, use database)
# Each session gets its own processor
sessions_data = {}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()
    return session['session_id']

def get_session_data(session_id):
    """Get session data (processor, history, etc)"""
    if session_id not in sessions_data:
        sessions_data[session_id] = {
            'processor': None,
            'qa_engine': None,
            'current_document': None,
            'history': []
        }
    return sessions_data[session_id]

session_visitors = {}

def get_visitor_state(session_id):
    """Track visitor name and conversation stage"""
    if session_id not in session_visitors:
        session_visitors[session_id] = {
            'name': None,
            'stage': 'greeting'  # greeting → acknowledged → asking_questions
        }
    return session_visitors[session_id]

def is_task_question(text):
    """Detect if text is a task question, not a name"""
    question_words = ['what', 'status', 'task', 'project', 'blocked', 'due', 'when', 'which', 'T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9']
    
    text_lower = text.lower()
    
    # Check for question indicators
    has_question_word = any(word in text_lower for word in question_words)
    has_question_mark = '?' in text
    
    # If has question word or question mark = question
    if has_question_word or has_question_mark:
        return True
    
    # "My name is X" should NOT be treated as question
    if 'my name is' in text_lower or "i'm" in text_lower or 'i am' in text_lower or 'this is' in text_lower:
        return False
    
    # Very short (< 3 words) without question = likely a name
    if len(text.split()) < 3:
        return False
    
    return False

def is_exit_message(text):
    """Detect if user wants to end conversation"""
    exit_words = ['bye', 'goodbye', 'thanks', 'thank you', 'exit', 'quit', 'done', 'see you', 'take care', 'cheers']
    text_lower = text.lower().strip()
    
    return any(word in text_lower for word in exit_words)

def extract_name(text):
    """Extract name from various formats"""
    text = text.strip()
    
    # "My name is X" format
    if 'my name is' in text.lower():
        name = text.split('is')[-1].strip()
        return name
    
    # "I'm X" format
    if "i'm" in text.lower():
        name = text.split("i'm")[-1].strip()
        return name
    
    # "I am X" format
    if 'i am' in text.lower():
        name = text.split('am')[-1].strip()
        return name
    
    # "Call me X" format
    if 'call me' in text.lower():
        name = text.split('call me')[-1].strip()
        return name
    
    # "It's X" or "This is X" format
    if "it's" in text.lower():
        name = text.split("it's")[-1].strip()
        return name
    
    # "X here" format
    if 'here' in text.lower():
        name = text.split('here')[0].strip()
        return name
    
    # Default: assume entire text is name
    return text

# ============================================================
# ROUTES: Pages
# ============================================================

@app.route('/')
def index():
    """Main chat interface"""
    session_id = get_session_id()
    session_data = get_session_data(session_id)
    
    context = {
        'has_document': session_data['processor'] is not None,
        'document_name': session_data['current_document'],
        'history': session_data['history']
    }
    
    return render_template('index.html', **context)

# ============================================================
# ROUTES: API
# ============================================================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """For v1.0: tasks are pre-loaded. This endpoint not used."""
    return jsonify({
        'status': 'success',
        'message': 'Tasks already loaded'
    })


@app.route('/api/answer', methods=['POST'])
def answer_question():
    """Answer task questions with visitor name tracking"""
    try:
        if task_processor is None:
            return jsonify({
                'status': 'error',
                'message': 'Tasks not loaded. Please contact admin.'
            }), 400
        
        session_id = get_session_id()
        visitor_state = get_visitor_state(session_id)
        
        data = request.json
        user_input = data.get('question', '').strip()
        
        if not user_input:
            return jsonify({
                'status': 'error',
                'message': 'Please enter a message'
            }), 400
        
        # Stage 1: Get visitor name (but detect if they ask question instead)
        if visitor_state['stage'] == 'greeting':
            
            # Check if first message is actually a question
            if is_task_question(user_input):
                visitor_state['name'] = 'Friend'
                visitor_state['stage'] = 'acknowledged'
                
                print(f"\n📝 {visitor_state['name']} (auto) asked: {user_input}")
                
                qa_engine = QAEngine(task_processor)
                answer_text = qa_engine.answer(user_input)
                
                formatted_answer = f"{answer_text}\n\n(By the way, what's your name? I'd like to greet you properly!)"
                
                return jsonify({
                    'status': 'success',
                    'question': user_input,
                    'answer': formatted_answer,
                    'is_greeting': False
                })
            
            else:
                # First message is their name - extract it
                extracted_name = extract_name(user_input)
                visitor_state['name'] = extracted_name
                visitor_state['stage'] = 'acknowledged'
                
                return jsonify({
                    'status': 'success',
                    'question': user_input,
                    'answer': f"Nice to meet you, {extracted_name}! 👋 I'm here to help with task status. What project/task status would you like to know?",
                    'is_greeting': True
                })

        # Check if user wants to exit
        if is_exit_message(user_input):
            exit_response = f"Thanks for chatting, {visitor_state['name']}! 👋 Hope I helped. Feel free to come back anytime!"
            return jsonify({
                'status': 'success',
                'question': user_input,
                'answer': exit_response,
                'is_greeting': False,
                'is_exit': True
            })
        
        # Stage 2: Answer questions (name already captured)
        visitor_name = visitor_state['name']
        
        print(f"\n📝 {visitor_name} asked: {user_input}")
        
        qa_engine = QAEngine(task_processor)
        answer_text = qa_engine.answer(user_input)
        
        formatted_answer = f"Hi {visitor_name}, {answer_text}"
        
        return jsonify({
            'status': 'success',
            'question': user_input,
            'answer': formatted_answer,
            'is_greeting': False
        })
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history for this session"""
    try:
        session_id = get_session_id()
        session_data = get_session_data(session_id)
        
        return jsonify({
            'status': 'success',
            'history': session_data['history']
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/reset', methods=['POST'])
def reset_session():
    """Clear current document and history"""
    try:
        session_id = get_session_id()
        session_data = get_session_data(session_id)
        
        session_data['processor'] = None
        session_data['qa_engine'] = None
        session_data['current_document'] = None
        session_data['history'] = []
        
        return jsonify({
            'status': 'success',
            'message': 'Session cleared. Upload a new document to continue.'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Check if tasks are loaded"""
    try:
        return jsonify({
            'status': 'success',
            'has_document': task_processor is not None,
            'document_name': 'task_status.csv'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large"""
    return jsonify({
        'status': 'error',
        'message': 'File too large. Maximum size: 50MB'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

# Load tasks when app starts
with app.app_context():
    task_loaded = load_tasks()
    if not task_loaded:
        print("⚠️  Warning: Could not load tasks. Upload may not work.")

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║  TASK STATUS BOT Web Application     ║
    ║                                      ║
    ║  http://localhost:5000               ║
    ║                                      ║
    ║  Press Ctrl+C to stop                ║
    ╚══════════════════════════════════════╝
    """)
    
    app.run(debug=True, port=5000)