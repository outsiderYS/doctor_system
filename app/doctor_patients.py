from flask import url_for, jsonify
from app import db, app
from app.errors import bad_request
from app.models import Doctor, Patient, DoctorPatient
from app.auth import token_auth
from flask import request
import datetime

@app.route('/doctor_patient/<int:doctor_id>/<int:patient_id>', methods=['PUT'])
@token_auth.login_required
def creat_doctor_patients_list(doctor_id, patient_id):
    jsondate = {}
    doctor_patient = DoctorPatient.query.filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
    if not doctor_patient:
        now = datetime.datetime.now()
        nowdate = now.strftime("%Y-%m-%d")
        doctor_patients = DoctorPatient(doctor_id=doctor_id, patient_id=patient_id, date=nowdate)
        db.session.add(doctor_patients)
        db.session.commit()
        jsondate['code'] = 200
        jsondate['backref'] = '患者收藏添加成功'
    else:
        db.session.delete(doctor_patient)
        db.session.commit()
        jsondate['code'] = 200
        jsondate['backref'] = '患者收藏删除成功'
    return jsonify(jsondate)

@app.route('/doctor_patient/<int:doctor_id>', methods=['GET'])
@token_auth.login_required
def get_doctor_collect(doctor_id):

    collectlist = DoctorPatient.query.filter_by(doctor_id=doctor_id).all()
    jsondata = {}
    if collectlist:
        dict = []
        for i in collectlist:
            dictionary = {}
            dictionary['patient_id'] = i.patient_id
            dictionary['date'] = i.date
            dict.append(dictionary)
        jsondata['collect'] = dict
        jsondata['code'] = 200

    return jsonify(jsondata)