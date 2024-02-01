from flask import Flask, render_template, request, redirect, url_for
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

DATA_FILE = "moods_data.json"

def load_moods_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    else:
        return {}

def save_moods_data(moods_data):
    with open(DATA_FILE, "w") as file:
        json.dump(moods_data, file)

def plot_mood_chart(moods_data):
    if not moods_data:
        return None

    fig, ax = plt.subplots()

    for month, mood_data in moods_data.items():
        days = list(mood_data.keys())
        moods = list(mood_data.values())
        ax.plot(days, moods, marker='o', label=month)

    ax.set_title('Mood Chart')
    ax.set_xlabel('Day')
    ax.set_ylabel('Mood Level')
    ax.legend()

    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode()
    plt.close()

    return f'<img src="data:image/png;base64,{plot_data}" alt="Mood Chart">'

@app.route('/')
def index():
    moods_data = load_moods_data()
    chart_html = plot_mood_chart(moods_data)
    return render_template('index.html', moods=moods_data, chart_html=chart_html)

@app.route('/add_mood', methods=['POST'])
def add_mood():
    moods_data = load_moods_data()

    for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']:
        for day in range(1, 32):
            key = f"{month}_{day}"
            mood_str = request.form.get(key, '')
            
            if mood_str.isdigit():
                mood = int(mood_str)
                if month not in moods_data:
                    moods_data[month] = {}
                moods_data[month][day] = mood

    save_moods_data(moods_data)

    return redirect(url_for('index'))

@app.route('/clear_history', methods=['POST'])
def clear_history():
    os.remove(DATA_FILE)
    return redirect(url_for('index'))

app.run(debug=False)