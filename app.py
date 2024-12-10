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

def init_db():
    try:
        with app.app_context():
            db = get_db()
            if db is None:
                logger.error("Could not connect to database for initialization")
                return False
            
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
            logger.info("Database initialized successfully")
            return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

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
    db = get_db()
    if not db:
        return "Error: Could not connect to database.", 500
    
    try:
        contacts = db.execute('''
            SELECT DISTINCT sender AS name FROM ChatMessages 
            UNION SELECT DISTINCT from_to AS name FROM SMS
        ''').fetchall()
        return render_template('main_menu.html', contacts=contacts)
    except sqlite3.Error as e:
        logger.error(f"Database error in index route: {e}")
        return "Error: Could not fetch contacts.", 500

# Chat route
@app.route('/chat/<name>')
def chat(name):
    db = get_db()
    if not db:
        return "Error: Could not connect to database.", 500
    
    try:
        messages = db.execute(
            'SELECT * FROM ChatMessages WHERE sender = ? ORDER BY time', 
            (name,)
        ).fetchall()
        return render_template('chat.html', name=name, messages=messages)
    except sqlite3.Error as e:
        logger.error(f"Database error in chat route: {e}")
        return "Error: Could not fetch messages.", 500

# SMS route
@app.route('/sms/<name>')
def sms_thread(name):
    db = get_db()
    if not db:
        return "Error: Could not connect to database.", 500
    
    try:
        sms_messages = db.execute(
            'SELECT * FROM SMS WHERE from_to = ? ORDER BY time', 
            (name,)
        ).fetchall()
        return render_template('sms.html', name=name, sms_messages=sms_messages)
    except sqlite3.Error as e:
        logger.error(f"Database error in sms route: {e}")
        return "Error: Could not fetch SMS messages.", 500

# Calls route
@app.route('/calls')
def calls():
    db = get_db()
    if not db:
        return "Error: Could not connect to database.", 500
    
    try:
        call_logs = db.execute('SELECT * FROM Calls ORDER BY time DESC').fetchall()
        return render_template('calls.html', call_logs=call_logs)
    except sqlite3.Error as e:
        logger.error(f"Database error in calls route: {e}")
        return "Error: Could not fetch call logs.", 500

# Keylogs route
@app.route('/keylogs')
def keylogs():
    db = get_db()
    if not db:
        return "Error: Could not connect to database.", 500
    
    try:
        keylogs = db.execute('SELECT * FROM Keylogs ORDER BY time DESC').fetchall()
        return render_template('keylogs.html', keylogs=keylogs)
    except sqlite3.Error as e:
        logger.error(f"Database error in keylogs route: {e}")
        return "Error: Could not fetch keylogs.", 500

# Installed Apps route
@app.route('/installed_apps')
def installed_apps():
    db = get_db()
    if not db:
        return "Error: Could not connect to database.", 500
    
    try:
        installed_apps = db.execute(
            'SELECT * FROM InstalledApps ORDER BY install_date DESC'
        ).fetchall()
        return render_template('installed_apps.html', installed_apps=installed_apps)
    except sqlite3.Error as e:
        logger.error(f"Database error in installed_apps route: {e}")
        return "Error: Could not fetch installed apps.", 500

# Contacts route
@app.route('/contacts')
def contacts_list():
    db = get_db()
    if not db:
        return "Error: Could not connect to database.", 500
    
    try:
        contacts = db.execute('SELECT * FROM Contacts ORDER BY name').fetchall()
        return render_template('contacts.html', contacts=contacts)
    except sqlite3.Error as e:
        logger.error(f"Database error in contacts route: {e}")
        return "Error: Could not fetch contacts.", 500

# Search functionality
@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')
    if not search_term:
        return jsonify({'error': 'Search term is required.'}), 400

    db = get_db()
    if not db:
        return jsonify({'error': 'Could not connect to database'}), 500

    try:
        # Search messages
        chat_results = db.execute(
            "SELECT sender, text, time FROM ChatMessages WHERE text LIKE ? ORDER BY time DESC",
            ('%' + search_term + '%',)
        ).fetchall()

        sms_results = db.execute(
            "SELECT from_to, text, time FROM SMS WHERE text LIKE ? ORDER BY time DESC",
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

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        if init_db():
            logger.info("Database created and initialized")
        else:
            logger.error("Failed to initialize database")
            exit(1)
    app.run(host='0.0.0.0', port=5000, debug=True)