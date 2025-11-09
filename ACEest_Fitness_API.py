from flask import Flask, request, jsonify, send_file
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

app = Flask(__name__)

# ---------------------- GLOBAL DATA ----------------------
workouts = {"Warm-up": [], "Workout": [], "Cool-down": []}
user_info = {}
MET_VALUES = {"Warm-up": 3, "Workout": 6, "Cool-down": 2.5}

# ---------------------- ENDPOINTS ----------------------

@app.route('/user_info', methods=['POST'])
def save_user_info():
    """Save user personal info for BMI/BMR calculations."""
    global user_info
    data = request.get_json()

    required = ["name", "age", "gender", "height", "weight"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required user info fields"}), 400

    try:
        height_cm = float(data["height"])
        weight_kg = float(data["weight"])
        age = int(data["age"])
        gender = data["gender"].upper()

        bmi = weight_kg / ((height_cm / 100) ** 2)
        if gender == "M":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

        user_info = {
            "name": data["name"],
            "age": age,
            "gender": gender,
            "height": height_cm,
            "weight": weight_kg,
            "bmi": round(bmi, 2),
            "bmr": round(bmr, 2),
        }
        return jsonify({"message": "User info saved successfully", "user_info": user_info}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/add_workout', methods=['POST'])
def add_workout():
    """Add a workout entry."""
    data = request.get_json()
    category = data.get("category")
    exercise = data.get("exercise")
    duration = data.get("duration")

    if not all([category, exercise, duration]):
        return jsonify({"error": "Missing fields: category, exercise, duration"}), 400

    try:
        duration = int(duration)
        weight = user_info.get("weight", 70)
        met = MET_VALUES.get(category, 5)
        calories = (met * 3.5 * weight / 200) * duration

        entry = {
            "exercise": exercise,
            "duration": duration,
            "calories": round(calories, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        workouts.setdefault(category, []).append(entry)
        return jsonify({"message": f"{exercise} added to {category}", "entry": entry}), 201
    except ValueError:
        return jsonify({"error": "Duration must be an integer"}), 400


@app.route('/workouts', methods=['GET'])
def get_workouts():
    """Return all workouts."""
    return jsonify(workouts)


@app.route('/summary', methods=['GET'])
def get_summary():
    """Return a summary with total time and calories."""
    total_time = 0
    total_calories = 0
    for cat, entries in workouts.items():
        for e in entries:
            total_time += e["duration"]
            total_calories += e["calories"]

    return jsonify({
        "total_minutes": total_time,
        "total_calories": round(total_calories, 2),
        "entries_count": sum(len(v) for v in workouts.values()),
        "by_category": {cat: len(v) for cat, v in workouts.items()}
    })


@app.route('/export_pdf', methods=['GET'])
def export_pdf():
    """Generate a simple weekly report as a downloadable PDF."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, height - 50, "ACEest Fitness Report")

    y = height - 100
    pdf.setFont("Helvetica", 12)

    # User Info
    if user_info:
        pdf.drawString(50, y, f"Name: {user_info['name']} | Age: {user_info['age']} | Gender: {user_info['gender']}")
        y -= 20
        pdf.drawString(50, y, f"Height: {user_info['height']} cm | Weight: {user_info['weight']} kg | BMI: {user_info['bmi']} | BMR: {user_info['bmr']}")
        y -= 40

    for cat, entries in workouts.items():
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(50, y, f"{cat} Workouts:")
        y -= 20
        pdf.setFont("Helvetica", 11)
        if not entries:
            pdf.drawString(60, y, "No sessions recorded.")
            y -= 20
        for e in entries:
            pdf.drawString(60, y, f"- {e['exercise']} | {e['duration']} min | {e['calories']} kcal | {e['timestamp']}")
            y -= 15
            if y < 100:
                pdf.showPage()
                y = height - 100
                pdf.setFont("Helvetica", 11)

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="ACEest_Fitness_Report.pdf", mimetype='application/pdf')


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "ACEest Fitness API is running!", "endpoints": ["/user_info", "/add_workout", "/workouts", "/summary", "/export_pdf"]})

# ---------------------- MAIN ----------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
