from flask import Flask, render_template, send_from_directory, request, jsonify, g
import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')

# Database configuration
DATABASE = 'data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        try:
            db = g._database = sqlite3.connect(DATABASE)
            db.row_factory = sqlite3.Row  # Access columns by name
            logger.info("Successfully connected to database")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            return None
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Main menu route
@app.route('/')
def index():
    conn = get_db()
    if conn:
        contacts = conn.execute('''
            SELECT DISTINCT sender AS name FROM ChatMessages 
            UNION SELECT DISTINCT from_to AS name FROM SMS
        ''').fetchall()
    else:
        contacts = []
    return render_template('main_menu.html', contacts=contacts)

# Chat route
@app.route('/chat/<name>')
def chat(name):
    conn = get_db()
    if conn:
        messages = conn.execute(
            'SELECT * FROM ChatMessages WHERE sender = ? ORDER BY time', 
            (name,)
        ).fetchall()
    else:
        messages = []
    return render_template('chat.html', name=name, messages=messages)

# SMS route
@app.route('/sms/<name>')
def sms_thread(name):
    conn = get_db()
    if conn:
        sms_messages = conn.execute(
            'SELECT * FROM SMS WHERE from_to = ? ORDER BY time', 
            (name,)
        ).fetchall()
    else:
        sms_messages = []
    return render_template('sms.html', name=name, sms_messages=sms_messages)

# Calls route
@app.route('/calls')
def calls():
    conn = get_db()
    if conn:
        call_logs = conn.execute('SELECT * FROM Calls ORDER BY time').fetchall()
        return render_template('calls.html', call_logs=call_logs)
    return "Error: Could not connect to the database.", 500

# Keylogs route
@app.route('/keylogs')
def keylogs():
    conn = get_db()
    if conn:
        keylogs = conn.execute('SELECT * FROM Keylogs ORDER BY time').fetchall()
        return render_template('keylogs.html', keylogs=keylogs)
    return "Error: Could not connect to the database.", 500

# Installed Apps route
@app.route('/installed_apps')
def installed_apps():
    conn = get_db()
    if conn:
        installed_apps = conn.execute('SELECT * FROM InstalledApps ORDER BY install_date').fetchall()
        return render_template('installed_apps.html', installed_apps=installed_apps)
    return "Error: Could not connect to the database.", 500

# Contacts route
@app.route('/contacts')
def contacts_list():
    conn = get_db()
    if conn:
        contacts = conn.execute('SELECT * FROM Contacts ORDER BY name').fetchall()
        return render_template('contacts.html', contacts=contacts)
    return "Error: Could not connect to the database.", 500


# Search functionality
@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')
    if not search_term:
        return jsonify({'error': 'Search term is required.'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Could not connect to database'}), 500

    try:
        # Search messages
        chat_results = conn.execute(
            "SELECT sender, text, time FROM ChatMessages WHERE text LIKE ? ORDER BY time",
            ('%' + search_term + '%',)
        ).fetchall()

        sms_results = conn.execute(
            "SELECT from_to, text, time FROM SMS WHERE text LIKE ? ORDER BY time",
            ('%' + search_term + '%',)
        ).fetchall()

        results = []
        for result in chat_results:
            results.append({
                'type': 'chat',
                'name': result['sender'],
                'text': result['text'],
                'time': result['time']
            })
        for result in sms_results:
            results.append({
                'type': 'sms',
                'name': result['from_to'],
                'text': result['text'],
                'time': result['time']
            })

        return jsonify(results)
    except sqlite3.Error as e:
        logger.error(f"Database error in search route: {e}")
        return jsonify({'error': str(e)}), 500

# Debug route to examine database schema
@app.route('/debug/db-schema')
def debug_schema():
    db = get_db()
    if not db:
        return "Could not connect to database", 500
    
    try:
        # Get all tables
        tables = db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """).fetchall()
        
        schema_info = {}
        # Get schema for each table
        for table in tables:
            table_name = table['name']
            columns = db.execute(f"PRAGMA table_info({table_name})").fetchall()
            schema_info[table_name] = [
                {'name': col['name'], 
                 'type': col['type'],
                 'notnull': col['notnull'],
                 'pk': col['pk']} 
                for col in columns
            ]
        
        return jsonify(schema_info)
    except sqlite3.Error as e:
        logger.error(f"Error getting schema: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)