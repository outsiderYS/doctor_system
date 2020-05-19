from flask import url_for, jsonify
from app import db, app
from app.errors import bad_request
from app.models import Patient, Doctor, Hospital
from app.auth import token_auth
from flask import request

@app.route('/patients/<int:id>', methods=['GET'])
@token_auth.login_required
def get_patient(id):
    patient = Patient.query.get_or_404(id)
    jsondata = patient.to_dict()
    digs = patient.dignosislists
    if not digs:
        return jsonify({})
    lists = []
    for i in digs:
        doctor = Doctor.query.get(i.doctor_id)
        doctor_name = doctor.name
        hospital_name = Hospital.query.get(doctor.hospital_id).name
        dict = i.to_dict()
        dict["doctor_name"] = doctor_name
        dict["hospital_name"] = hospital_name
        lists.append(dict)
    jsondata['records'] = lists
    return jsonify(jsondata)

@app.route('/patients/<userid>', methods=['GET'])
@token_auth.login_required
def get_patient_info(userid):
    patient = Patient.query.filter_by(userid=userid).first()
    return jsonify({
        'code': 200,
        'name': patient.name
    })