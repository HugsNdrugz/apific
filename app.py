from flask import Flask, render_template

app = Flask(__name__)

# Sample static data for testing
contacts = [
    {"name": "John Doe", "last_message": "Hey there!"},
    {"name": "Jane Smith", "last_message": "See you tomorrow!"}
]

@app.route('/')
def index():
    return render_template('main_menu.html', contacts=contacts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)