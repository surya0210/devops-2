from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# In-memory data
workouts = []
diet_plans = {
    "Weight Loss": ["Oatmeal + Fruits", "Grilled Chicken Salad", "Vegetable Soup", "Brown Rice & Veggies"],
    "Muscle Gain": ["Egg Omelet", "Chicken Breast + Quinoa", "Protein Shake", "Greek Yogurt + Nuts"],
    "Endurance": ["Banana + Peanut Butter", "Whole Grain Pasta", "Sweet Potatoes", "Salmon & Avocado"]
}

# Home page
@app.route('/')
def home():
    html = "<h1>🏋️ ACEest Fitness & Gym Tracker</h1>"
    html += "<h3>Add Workout</h3>"
    html += '''
        <form action="/add" method="post">
            Exercise: <input type="text" name="exercise" required><br><br>
            Duration (min): <input type="number" name="duration" required><br><br>
            Category: 
            <select name="category">
                <option>Warm-up</option>
                <option>Workout</option>
                <option>Cool-down</option>
            </select><br><br>
            <button type="submit">Add Session</button>
        </form>
        <br><a href="/summary">📊 View Summary</a> | 
        <a href="/diet">🥗 View Diet Chart</a>
    '''
    if workouts:
        html += "<h3>Workout Log</h3><table border='1' cellpadding='8'><tr><th>Exercise</th><th>Duration</th><th>Category</th><th>Timestamp</th></tr>"
        for w in workouts:
            html += f"<tr><td>{w['exercise']}</td><td>{w['duration']}</td><td>{w['category']}</td><td>{w['timestamp']}</td></tr>"
        html += "</table>"
    else:
        html += "<p>No workouts logged yet!</p>"
    return html

# Add workout
@app.route('/add', methods=['POST'])
def add_workout():
    exercise = request.form['exercise']
    duration = int(request.form['duration'])
    category = request.form['category']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    workouts.append({
        "exercise": exercise,
        "duration": duration,
        "category": category,
        "timestamp": timestamp
    })
    return '''
        <h3>✅ Workout added successfully!</h3>
        <a href="/">← Back</a>
    '''

# Diet chart
@app.route('/diet')
def diet():
    html = "<h1>🥗 ACEest Fitness Diet Chart</h1>"
    for goal, foods in diet_plans.items():
        html += f"<h3>{goal}</h3><ul>"
        for food in foods:
            html += f"<li>{food}</li>"
        html += "</ul>"
    html += "<br><a href='/'>← Back</a>"
    return html

# Workout summary
@app.route('/summary')
def summary():
    total_time = sum([w["duration"] for w in workouts])
    cat_summary = {}
    for w in workouts:
        cat_summary[w["category"]] = cat_summary.get(w["category"], 0) + w["duration"]

    html = "<h1>📊 Workout Summary</h1>"
    html += f"<p><strong>Total Duration:</strong> {total_time} minutes</p>"
    html += "<table border='1' cellpadding='8'><tr><th>Category</th><th>Total Time (min)</th></tr>"
    for cat, total in cat_summary.items():
        html += f"<tr><td>{cat}</td><td>{total}</td></tr>"
    html += "</table>"
    html += "<br><a href='/'>← Back</a>"
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
