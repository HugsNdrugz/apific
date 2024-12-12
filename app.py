
from flask import Flask, render_template, request, jsonify
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Database configuration
DATABASE = 'data.db'

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return None

@app.route('/')
def index():
    """Handle main page route"""
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500
        
    try:
        contacts = conn.execute('''
            SELECT DISTINCT 
                c.name,
                COALESCE(
                    (SELECT text FROM ChatMessages 
                     WHERE sender = c.name 
                     ORDER BY time DESC LIMIT 1),
                    (SELECT text FROM SMS 
                     WHERE from_to = c.name 
                     ORDER BY time DESC LIMIT 1)
                ) as last_message,
                COALESCE(
                    (SELECT time FROM ChatMessages 
                     WHERE sender = c.name 
                     ORDER BY time DESC LIMIT 1),
                    (SELECT time FROM SMS 
                     WHERE from_to = c.name 
                     ORDER BY time DESC LIMIT 1)
                ) as time
            FROM (
                SELECT DISTINCT sender as name FROM ChatMessages 
                UNION 
                SELECT DISTINCT from_to FROM SMS
            ) c
        ''').fetchall()
        return render_template('main_menu.html', contacts=[dict(c) for c in contacts])
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return "Error fetching contacts", 500
    finally:
        conn.close()

@app.route('/chat/<name>')
def chat(name):
    """Handle individual chat route"""
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500
        
    try:
        messages = conn.execute(
            'SELECT * FROM ChatMessages WHERE sender = ? ORDER BY time', 
            (name,)
        ).fetchall()
        return render_template('chat.html', name=name, messages=messages)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return "Error fetching messages", 500
    finally:
        conn.close()

@app.route('/calls')
def calls():
    """Handle calls route"""
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500
        
    try:
        call_logs = conn.execute('SELECT * FROM Calls ORDER BY time DESC').fetchall()
        return render_template('calls.html', call_logs=call_logs)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return "Error fetching calls", 500
    finally:
        conn.close()

@app.route('/keylogs')
def keylogs():
    """Handle keylogs route"""
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500
        
    try:
        keylog_data = conn.execute('SELECT * FROM Keylogs ORDER BY time DESC').fetchall()
        return render_template('keylogs.html', keylogs=keylog_data)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return "Error fetching keylogs", 500
    finally:
        conn.close()

@app.route('/search', methods=['POST'])
def search():
    """Handle search functionality"""
    search_term = request.form.get('search_term')
    if not search_term:
        return jsonify({'error': 'Search term required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection error'}), 500

    try:
        # Search in both chat messages and SMS
        chat_results = conn.execute('''
            SELECT 'chat' as type, sender as name, text, time 
            FROM ChatMessages 
            WHERE text LIKE ? 
            ORDER BY time DESC LIMIT 25
        ''', ('%' + search_term + '%',)).fetchall()

        sms_results = conn.execute('''
            SELECT 'sms' as type, from_to as name, text, time 
            FROM SMS 
            WHERE text LIKE ? 
            ORDER BY time DESC LIMIT 25
        ''', ('%' + search_term + '%',)).fetchall()

        results = [dict(row) for row in (chat_results + sms_results)]
        return jsonify(results)
    except sqlite3.Error as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
