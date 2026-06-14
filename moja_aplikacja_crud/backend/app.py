from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Tabela dla checklisty
        cur.execute('''
            CREATE TABLE IF NOT EXISTS checklist_items (
                id SERIAL PRIMARY KEY,
                text VARCHAR(255) NOT NULL,
                checked BOOLEAN DEFAULT FALSE,
                data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela dla zadań
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                nazwa VARCHAR(255) NOT NULL,
                data_zakonczenia DATE,
                data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela dla notatek
        cur.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                tytul VARCHAR(255) NOT NULL,
                tekst TEXT,
                data_utworzenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB init error: {e}")

init_db()

# === CHECKLISTA 

@app.route('/api/checklist', methods=['GET'])
def get_checklist():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, text, checked FROM checklist_items ORDER BY data_utworzenia DESC')
        items = [{'id': row[0], 'text': row[1], 'checked': row[2]} for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({'items': items}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/checklist', methods=['POST'])
def add_checklist_item():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Tekst jest wymagany'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO checklist_items (text) VALUES (%s) RETURNING id', (text,))
        item_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'id': item_id, 'text': text, 'checked': False}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/checklist/<int:id>', methods=['PUT'])
def toggle_checklist_item(id):
    try:
        data = request.get_json()
        checked = data.get('checked')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE checklist_items SET checked = %s WHERE id = %s', (checked, id))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'status': 'updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/checklist/<int:id>', methods=['DELETE'])
def delete_checklist_item(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM checklist_items WHERE id = %s', (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- ZADANIA

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, nazwa, data_zakonczenia FROM tasks ORDER BY data_zakonczenia ASC NULLS LAST')
        items = [{'id': row[0], 'nazwa': row[1], 'data_zakonczenia': str(row[2]) if row[2] else None} for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({'tasks': items}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def add_task():
    try:
        data = request.get_json()
        nazwa = data.get('nazwa', '').strip()
        data_zakonczenia = data.get('data_zakonczenia')
        
        if not nazwa:
            return jsonify({'error': 'Nazwa jest wymagana'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO tasks (nazwa, data_zakonczenia) VALUES (%s, %s) RETURNING id', 
                   (nazwa, data_zakonczenia if data_zakonczenia else None))
        task_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'id': task_id, 'nazwa': nazwa, 'data_zakonczenia': data_zakonczenia}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    try:
        data = request.get_json()
        nazwa = data.get('nazwa')
        data_zakonczenia = data.get('data_zakonczenia')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        if nazwa:
            cur.execute('UPDATE tasks SET nazwa = %s WHERE id = %s', (nazwa, id))
        if data_zakonczenia is not None:
            cur.execute('UPDATE tasks SET data_zakonczenia = %s WHERE id = %s', (data_zakonczenia, id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'status': 'updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM tasks WHERE id = %s', (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- NOTATNKI

@app.route('/api/notes', methods=['GET'])
def get_notes():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, tytul, tekst FROM notes ORDER BY data_utworzenia DESC')
        items = [{'id': row[0], 'tytul': row[1], 'tekst': row[2]} for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({'notes': items}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes', methods=['POST'])
def add_note():
    try:
        data = request.get_json()
        tytul = data.get('tytul', '').strip()
        tekst = data.get('tekst', '').strip()
        
        if not tytul:
            return jsonify({'error': 'Tytuł jest wymagany'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO notes (tytul, tekst) VALUES (%s, %s) RETURNING id', (tytul, tekst))
        note_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'id': note_id, 'tytul': tytul, 'tekst': tekst}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:id>', methods=['PUT'])
def update_note(id):
    try:
        data = request.get_json()
        tytul = data.get('tytul')
        tekst = data.get('tekst')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        if tytul:
            cur.execute('UPDATE notes SET tytul = %s WHERE id = %s', (tytul, id))
        if tekst is not None:
            cur.execute('UPDATE notes SET tekst = %s WHERE id = %s', (tekst, id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'status': 'updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM notes WHERE id = %s', (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)