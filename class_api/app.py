import os
from flask import Flask, jsonify, request

app = Flask(__name__)

students = [{"id":1,"FN":"Ali","LN":"Mastouri","reports":[{"Title":"Bla Bla", "Type":"Mini Senior Project"}]}]

@app.get('/students')
def get_students():
    return {"students": students}

@app.post('/students')
def add_student():
    request_data = request.get_json()
    new_student = {
        "id": len(students) + 1,
        "FN": request_data.get("FN"),
        "LN": request_data.get("LN"),
        "reports": request_data.get("reports", [])
    }
    students.append(new_student)
    return {"message": "Student added successfully", "student": new_student}, 201

@app.post('/students/<int:student_id>/reports')
def add_report(student_id):
    request_data = request.get_json()
    student = next((s for s in students if s["id"] == student_id), None)
    if student is None:
        return {"message": "Student not found"}, 404

    new_report = {
        "Title": request_data.get("Title"),
        "Type": request_data.get("Type")
    }
    student["reports"].append(new_report)
    return {"message": "Report added successfully", "report": new_report}, 201

@app.get('/students/<int:student_id>')
def get_student(student_id):
    for student in students:
        if student["id"] == student_id:
            return {"student": student}
    return {"message": "Student not found"}, 404

@app.get('/students/<int:student_id>/reports')
def get_student_reports(student_id):
    for student in students:
        if student["id"] == student_id:
            return {"reports": student["reports"]}
    return {"message": "Student not found"}, 404

# Port comes from the PORT environment variable (default 5001).
# host 0.0.0.0 is required so the API is reachable from outside the container.
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")