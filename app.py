import os
from flask import Flask, jsonify, render_template, send_from_directory

# Определяем абсолютный путь к директории приложения
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__,
            template_folder=os.path.join(basedir, 'templates'),
            static_folder=os.path.join(basedir, 'static'))

# Путь к файлу с данными
JSON_FILE = os.path.join(basedir, 'output', 'categorized_links.json')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    if not os.path.exists(JSON_FILE):
        return jsonify({"error": "Data file not found. Please run the processing script first."}), 404
    return send_from_directory('output', 'categorized_links.json')

if __name__ == '__main__':
    app.run(debug=True)
