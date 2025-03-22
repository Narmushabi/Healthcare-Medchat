from flask import Flask, request, jsonify, session, send_from_directory
import os
import sqlite3
import uuid
import hashlib
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from langchain_community.llms import Together
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

import os
from dotenv import load_dotenv

# Load .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Verify if environment variables are loaded
print("FLASK_SECRET_KEY:", os.getenv("FLASK_SECRET_KEY"))  # Should print a value, NOT None
print("TOGETHER_API_KEY:", os.getenv("TOGETHER_API_KEY"))  # Should print a value, NOT None
print("UPLOAD_FOLDER:", os.getenv("UPLOAD_FOLDER"))  # Should print a value, NOT None

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'super-secret-key')  # Uses .env value

# AI Model Setup
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY', '')
llm = Together(
    model="meta-llama/Llama-3-8b-chat-hf",
    together_api_key=TOGETHER_API_KEY,  # Uses .env value
    temperature=0.7,
    max_tokens=512
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per minute"],
    storage_uri="memory://"
)
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory, verbose=True)

# Database Setup
DB_PATH = 'medichat.db'

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        message TEXT NOT NULL,
        sender TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    """Hash passwords using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Authentication Routes
@app.route('/signup', methods=['POST'])
def signup():
    """Register a new user"""
    data = request.json
    email, password = data.get('email'), data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email already exists"}), 400

        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        cursor.execute("INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)",
                       (user_id, email, password_hash))
        conn.commit()
        return jsonify({"message": "User registered successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.json
    email, password = data.get('email'), data.get('password')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user or user[1] != hash_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    session['user_id'] = user[0]
    return jsonify({"message": "Login successful", "user_id": user[0]})

@app.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({"message": "Logged out"})

# Chat Route
@app.route('/chat', methods=['POST'])
def chat():
    """Handle user chat with AI"""
    data = request.json
    user_message = data.get('message')

    response = conversation.predict(input=user_message)
    return jsonify({"response": response})

# Document Upload
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_document():
    """Upload user documents"""
    if 'document' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['document']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify({"message": "File uploaded successfully", "filename": filename})

# Serve Uploaded Files
@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)

