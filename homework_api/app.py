import os
from flask import Flask, request, jsonify
from errors import APIError
from models import Report, Student, require_str
from auth import (create_access_token, create_refresh_token, verify_refresh_token,
                  token_required, USERNAME, PASSWORD, ACCESS_TOKEN_MINUTES)

app = Flask(__name__)

# ---- Phase 2 storage: dictionaries (key = ID) ----
reports = {}
next_report_id = 1

students = {}
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

# ---- Authentication ----
@app.post("/login")
def login():
    data = get_json_body()
    username = require_str(data, "username")
    password = require_str(data, "password")

    if username != USERNAME or password != PASSWORD:
        raise APIError("Invalid username or password", 401)

    return jsonify({
        "access_token": create_access_token(username),
        "refresh_token": create_refresh_token(username),
        "expires_in": ACCESS_TOKEN_MINUTES * 60
    }), 200


@app.post("/refresh")
def refresh():
    data = get_json_body()
    token = require_str(data, "refresh_token")
    username = verify_refresh_token(token)

    return jsonify({
        "access_token": create_access_token(username),
        "expires_in": ACCESS_TOKEN_MINUTES * 60
    }), 200

# ---- Report endpoints ----
@app.post("/reports")
def create_report():
    global next_report_id
    data = get_json_body()
    report = Report.from_json(data, next_report_id)
    reports[report.ID_R] = report          # the ID is the key
    next_report_id += 1
    return jsonify(report.to_dict()), 201


@app.get("/reports")
def get_reports():
    return jsonify([r.to_dict() for r in reports.values()]), 200


@app.get("/reports/<int:report_id>")
def get_report(report_id):
    if report_id not in reports:
        raise APIError(f"Report {report_id} not found", 404)
    return jsonify(reports[report_id].to_dict()), 200


# ---- Student endpoints ----
@app.post("/students")
def create_student():
    global next_student_id
    data = get_json_body()
    student = Student.from_json(data, next_student_id)

    # The report this student points to must already exist
    if student.ID_R not in reports:
        raise APIError(f"Report {student.ID_R} not found", 404)

    students[student.ID_S] = student       # the ID is the key
    next_student_id += 1
    return jsonify(student.to_dict()), 201


@app.get("/students")
@token_required
def get_students():
    return jsonify([s.to_dict() for s in students.values()]), 200


@app.get("/students/<int:student_id>")
@token_required
def get_student(student_id):
    if student_id not in students:
        raise APIError(f"Student {student_id} not found", 404)
    return jsonify(students[student_id].to_dict()), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # host 0.0.0.0 is required in Docker, otherwise the API is unreachable from outside the container
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")