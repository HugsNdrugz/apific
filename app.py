from flask import Flask, render_template, send_from_directory, request, jsonify
import sqlite3
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app with template configuration
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static',
           static_url_path='/static')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE = 'data.db'

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # Access columns by name
        # Verify connection by executing a test query
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        logger.info(f"Connected to database. Available tables: {[table[0] for table in tables]}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return None

@app.route('/')
def index():
    conn = get_db_connection()
    if conn:
        try:
            # Fetch distinct contacts and their latest messages
            contacts = conn.execute('''
                SELECT DISTINCT c.name,
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
            
            # Convert Row objects to dictionaries
            contacts_list = [dict(contact) for contact in contacts]
            conn.close()
            return render_template('main_menu.html', contacts=contacts_list)
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return "Error fetching contacts", 500
    return "Database connection error", 500

@app.route('/chat/<name>')
def chat(name):
    conn = get_db_connection()
    if conn:
        try:
            messages = conn.execute(
                'SELECT * FROM ChatMessages WHERE sender = ? ORDER BY time', (name,)
            ).fetchall()
            conn.close()
            return render_template('chat.html', name=name, messages=messages)
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return "Error fetching messages", 500
    return "Database connection error", 500

@app.route('/sms/<name>')
def sms_thread(name):
    conn = get_db_connection()
    if conn:
        try:
            sms_messages = conn.execute(
                'SELECT * FROM SMS WHERE from_to = ? ORDER BY time', (name,)
            ).fetchall()
            conn.close()
            return render_template('sms.html', name=name, sms_messages=sms_messages)
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return "Error fetching SMS", 500
    return "Database connection error", 500

@app.route('/calls')
def calls():
    conn = get_db_connection()
    if conn:
        try:
            call_logs = conn.execute('SELECT * FROM Calls ORDER BY time DESC').fetchall()
            conn.close()
            return render_template('calls.html', call_logs=call_logs)
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return "Error fetching calls", 500
    return "Database connection error", 500

@app.route('/keylogs')
def keylogs():
    conn = get_db_connection()
    if conn:
        try:
            keylog_data = conn.execute('SELECT * FROM Keylogs ORDER BY time DESC').fetchall()
            conn.close()
            return render_template('keylogs.html', keylogs=keylog_data)
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return "Error fetching keylogs", 500
    return "Database connection error", 500

@app.route('/installed_apps')
def installed_apps():
    conn = get_db_connection()
    if conn:
        try:
            app_data = conn.execute('SELECT * FROM InstalledApps ORDER BY application_name').fetchall()
            conn.close()
            return render_template('installed_apps.html', installed_apps=app_data)
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return "Error fetching installed apps", 500
    return "Database connection error", 500

@app.route('/contacts')
def contacts_list():
    conn = get_db_connection()
    if conn:
        try:
            contacts = conn.execute('SELECT * FROM Contacts ORDER BY name').fetchall()
            conn.close()
            return render_template('contacts.html', contacts=contacts)
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return "Error fetching contacts", 500
    return "Database connection error", 500

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')
    if not search_term:
        return jsonify({'error': 'Search term required'}), 400

    conn = get_db_connection()
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