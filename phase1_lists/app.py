from flask import Flask, request, jsonify
from errors import APIError
from models import Report, Student

app = Flask(__name__)

# ---- Phase 1 storage: plain lists ----
reports = []
next_report_id = 1

students = []
next_student_id = 1


# ---- Error handlers: always return JSON ----
@app.errorhandler(APIError)
def handle_api_error(e):
    return jsonify({"error": e.message}), e.status

@app.errorhandler(404)
def handle_404(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(405)
def handle_405(e):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(Exception)
def handle_500(e):
    return jsonify({"error": "Internal server error"}), 500


def get_json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise APIError("Request body must be a valid JSON object")
    return data


def report_exists(report_id):
    for r in reports:
        if r.ID_R == report_id:
            return True
    return False


# ---- Report endpoints ----
@app.post("/reports")
def create_report():
    global next_report_id
    data = get_json_body()
    report = Report.from_json(data, next_report_id)
    next_report_id += 1
    reports.append(report)
    return jsonify(report.to_dict()), 201


@app.get("/reports")
def get_reports():
    return jsonify([r.to_dict() for r in reports]), 200


@app.get("/reports/<int:report_id>")
def get_report(report_id):
    for r in reports:
        if r.ID_R == report_id:
            return jsonify(r.to_dict()), 200
    raise APIError(f"Report {report_id} not found", 404)


# ---- Student endpoints ----
@app.post("/students")
def create_student():
    global next_student_id
    data = get_json_body()
    student = Student.from_json(data, next_student_id)

    # The report this student points to must already exist
    if not report_exists(student.ID_R):
        raise APIError(f"Report {student.ID_R} not found", 404)

    next_student_id += 1
    students.append(student)
    return jsonify(student.to_dict()), 201


@app.get("/students")
def get_students():
    return jsonify([s.to_dict() for s in students]), 200


@app.get("/students/<int:student_id>")
def get_student(student_id):
    for s in students:
        if s.ID_S == student_id:
            return jsonify(s.to_dict()), 200
    raise APIError(f"Student {student_id} not found", 404)


if __name__ == "__main__":
    app.run(debug=True)