from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tables')
def get_tables():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Get record count for each table
        result = []
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table['name']};")
            count = cursor.fetchone()['count']
            result.append({
                'name': table['name'],
                'count': count
            })
            
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error getting tables: {str(e)}")
        return jsonify([]), 500
    finally:
        db.close()

@app.route('/api/relations')
def get_relations():
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        relations = {}
        for table in tables:
            table_name = table['name']
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Get primary key
            primary_key = next((col['name'] for col in columns if col['pk'] == 1), None)
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            foreign_keys = [fk['from'] for fk in cursor.fetchall()]
            
            relations[table_name] = {
                'primary_key': primary_key,
                'foreign_keys': foreign_keys
            }
            
        return jsonify(relations)
    except Exception as e:
        logging.error(f"Error getting relations: {str(e)}")
        return jsonify({}), 500
    finally:
        db.close()

@app.route('/api/table/<table_name>/<int:id>')
def get_record(table_name, id):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?;", (id,))
        record = cursor.fetchone()
        
        if record:
            return jsonify(dict(record))
        return jsonify({"error": "Record not found"}), 404
    except Exception as e:
        logging.error(f"Error getting record: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@app.route('/api/recent')
def get_recent():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        recent_records = []
        for table in tables:
            table_name = table['name']
            # Get the most recent records from each table
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 5;")
            records = cursor.fetchall()
            
            for record in records:
                recent_records.append({
                    'table': table_name,
                    'id': record['id'],
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return jsonify(sorted(recent_records, key=lambda x: x['timestamp'], reverse=True)[:20])
    except Exception as e:
        logging.error(f"Error getting recent records: {str(e)}")
        return jsonify([]), 500
    finally:
        db.close()

@app.route('/api/search')
def search():
    term = request.args.get('term', '').lower()
    if not term:
        return jsonify([])
        
    try:
        db = get_db()
        cursor = db.cursor()
        
        results = []
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table['name']
            cursor.execute(f"SELECT * FROM {table_name};")
            columns = [description[0] for description in cursor.description]
            
            for row in cursor.fetchall():
                for col in columns:
                    value = str(row[col]).lower()
                    if term in value:
                        results.append({
                            'table': table_name,
                            'id': row['id'],
                            'match': f"{col}: {value}"
                        })
                        break
                        
        return jsonify(results[:20])  # Limit to 20 results
    except Exception as e:
        logging.error(f"Error searching: {str(e)}")
        return jsonify([]), 500
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
