from flask import url_for, jsonify
from app import db, app
from app.errors import bad_request
from app.models import Doctor
from app.auth import token_auth
from flask import request

@app.route('/doctors/<int:id>', methods=['GET'])
@token_auth.login_required
def get_doctor(id):
    return jsonify(Doctor.query.get_or_404(id).to_dict())

@app.route('/doctors/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != doctor.username and Doctor.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    doctor.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(doctor.to_dict())

