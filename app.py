
from flask import Flask, render_template, request, jsonify
import sqlite3
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_db_connection():
    try:
        conn = sqlite3.connect('data.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None

@app.route('/')
def index():
    conn = get_db_connection()
    if conn:
        contacts = conn.execute('''
            SELECT DISTINCT 
                c.name,
                COALESCE(
                    (SELECT text FROM ChatMessages WHERE sender = c.name ORDER BY time DESC LIMIT 1),
                    (SELECT text FROM SMS WHERE from_to = c.name ORDER BY time DESC LIMIT 1)
                ) as last_message,
                COALESCE(
                    (SELECT time FROM ChatMessages WHERE sender = c.name ORDER BY time DESC LIMIT 1),
                    (SELECT time FROM SMS WHERE from_to = c.name ORDER BY time DESC LIMIT 1)
                ) as time
            FROM (
                SELECT DISTINCT sender as name FROM ChatMessages 
                UNION 
                SELECT DISTINCT from_to FROM SMS
            ) c
        ''').fetchall()
        conn.close()
        return render_template('main_menu.html', contacts=contacts)
    return "Database connection error", 500

@app.route('/chat/<name>')
def chat(name):
    conn = get_db_connection()
    if conn:
        messages = conn.execute('SELECT * FROM ChatMessages WHERE sender = ? ORDER BY time', (name,)).fetchall()
        conn.close()
        return render_template('chat.html', name=name, messages=messages)
    return "Database connection error", 500

@app.route('/calls')
def calls():
    conn = get_db_connection()
    if conn:
        call_logs = conn.execute('SELECT * FROM Calls ORDER BY time DESC').fetchall()
        conn.close()
        return render_template('calls.html', call_logs=call_logs)
    return "Database connection error", 500

@app.route('/keylogs')
def keylogs():
    conn = get_db_connection()
    if conn:
        keylog_data = conn.execute('SELECT * FROM Keylogs ORDER BY time DESC').fetchall()
        conn.close()
        return render_template('keylogs.html', keylogs=keylog_data)
    return "Database connection error", 500

@app.route('/contacts')
def contacts():
    conn = get_db_connection()
    if conn:
        contacts_data = conn.execute('SELECT * FROM Contacts ORDER BY name').fetchall()
        conn.close()
        return render_template('contacts.html', contacts=contacts_data)
    return "Database connection error", 500

@app.route('/sms/<name>')
def sms(name):
    conn = get_db_connection()
    if conn:
        try:
            sms_messages = conn.execute(
                'SELECT * FROM SMS WHERE from_to = ? ORDER BY time DESC',
                (name,)
            ).fetchall()
            return render_template('sms.html', name=name, sms_messages=sms_messages)
        except sqlite3.Error as e:
            logging.error(f"Database error in sms route: {e}")
            return "Database error", 500
        finally:
            conn.close()
    return "Database connection error", 500

@app.route('/installed_apps')
def installed_apps():
    conn = get_db_connection()
    if conn:
        try:
            apps = conn.execute('SELECT * FROM InstalledApps ORDER BY application_name').fetchall()
            return render_template('installed_apps.html', installed_apps=apps)
        except sqlite3.Error as e:
            logging.error(f"Database error in installed_apps: {e}")
            return "Database error", 500
        finally:
            conn.close()
    return "Database connection error", 500

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')
    if not search_term:
        return jsonify([])

    conn = get_db_connection()
    if conn:
        try:
            results = conn.execute('''
                SELECT 'chat' as type, sender as name, text, time 
                FROM ChatMessages 
                WHERE text LIKE ? 
                UNION ALL
                SELECT 'sms' as type, from_to as name, text, time 
                FROM SMS 
                WHERE text LIKE ?
                ORDER BY time DESC LIMIT 50
            ''', (f'%{search_term}%', f'%{search_term}%')).fetchall()
            return jsonify([dict(row) for row in results])
        finally:
            conn.close()
    return jsonify({'error': 'Database connection failed'}), 500


@app.route('/search_keylogs', methods=['POST'])
def search_keylogs():
    search_term = request.form.get('search_term')
    if not search_term:
        return jsonify([])

    conn = get_db_connection()
    if conn:
        try:
            results = conn.execute('''
                SELECT application, time, text
                FROM Keylogs 
                WHERE application LIKE ? OR text LIKE ?
                ORDER BY time DESC LIMIT 50
            ''', (f'%{search_term}%', f'%{search_term}%')).fetchall()
            return jsonify([dict(row) for row in results])
        finally:
            conn.close()
    return jsonify({'error': 'Database connection failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
