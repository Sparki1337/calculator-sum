from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///counter.db'
db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    message_count = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def parse_line(line):
    parts = line.split('-')
    if len(parts) >= 2:
        name = parts[0].strip()
        value_part = '-'.join(parts[1:]).strip()
        try:
            value = int(value_part)
            return name, value
        except ValueError:
            numbers = re.findall(r'-?\d+', value_part)
            if numbers:
                return name, int(numbers[-1])
    return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_message():
    if 'session_id' not in session:
        session['session_id'] = os.urandom(16).hex()
        session['message_count'] = 0
    
    data = request.json
    message = data.get('message', '')
    
    # Увеличиваем счетчик сообщений
    session['message_count'] = session.get('message_count', 0) + 1
    
    # Если счетчик больше 6, очищаем все данные
    if session['message_count'] > 6:
        Entry.query.filter_by(session_id=session['session_id']).delete()
        db.session.commit()
        session['message_count'] = 1
    
    # Обрабатываем сообщение
    lines = message.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        name, value = parse_line(line)
        if name and value is not None:
            existing_entry = Entry.query.filter_by(
                session_id=session['session_id'],
                name=name
            ).first()
            
            if existing_entry:
                existing_entry.value += value
            else:
                new_entry = Entry(
                    session_id=session['session_id'],
                    name=name,
                    value=value,
                    message_count=session['message_count']
                )
                db.session.add(new_entry)
    
    db.session.commit()
    
    # Формируем ответ
    entries = Entry.query.filter_by(session_id=session['session_id']).all()
    values = {entry.name: entry.value for entry in entries}
    
    response = {
        'values': values,
        'message_count': session['message_count'],
        'max_messages': 6
    }
    
    return jsonify(response)

@app.route('/api/clear', methods=['POST'])
def clear_data():
    if 'session_id' in session:
        Entry.query.filter_by(session_id=session['session_id']).delete()
        db.session.commit()
        session['message_count'] = 0
    return jsonify({'status': 'success'})

@app.route('/api/new_count', methods=['POST'])
def new_count():
    if 'session_id' in session:
        Entry.query.filter_by(session_id=session['session_id']).delete()
        db.session.commit()
        session['message_count'] = 0
    return jsonify({'status': 'success'})

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 