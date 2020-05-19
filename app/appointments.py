from flask import url_for, jsonify
from app import db, app
from app.errors import bad_request
from app.models import Appointment, Doctor, Patient
from app.auth import token_auth
from flask import request
import datetime

@app.route('/appointments/<int:id>/<date>', methods=['GET'])
@token_auth.login_required
def get_appointment(id, date):
    doctor = Doctor.query.get_or_404(id)
    appointment = doctor.appointments.filter_by(appointment_date=date).first()
    if not appointment:
        return jsonify({})
    jsondata = appointment.to_dict()
    jsondata['code'] = 200
    return jsonify(jsondata)

@app.route('/appointments/<int:id>/<int:num>', methods=['GET'])
@token_auth.login_required
def get_all_appointment(id, num):
    appointments = Appointment.query.filter_by(doctor_id=id).order_by(Appointment.appointment_date.desc()).all()[0:num]
    dict = {}
    dict['code'] = 200
    jsondata = []
    if not appointments:
        return jsonify({})
    for i in appointments:
        jsondata.append(i.to_dict())
    dict['list'] = jsondata
    return jsonify(dict)

@app.route('/appointments/<int:id>', methods=['PUT'])
@token_auth.login_required
def creat_appointment(id):
    data = request.get_json() or {}
    now = datetime.datetime.now()
    nowdate = now.strftime("%Y-%m-%d")
    for i in data['date']:
        if nowdate <= i:
            appointment = Appointment.query.filter_by(appointment_date=i).first()
            if appointment:
                appointment.am_appointment = data['am_appointment']
                appointment.pm_appointment = data['pm_appointment']
                appointment.cost = data['cost']
            else:
                appointment = Appointment(doctor_id=id, am_appointment=data['am_appointment'],
                                          pm_appointment=data['am_appointment'], cost=data['cost'])
                appointment.appointment_date = i
                db.session.add(appointment)
    db.session.commit()
    return jsonify({'code': 200})

@app.route('/appointments/orderlists/<int:id>/<period>', methods=['GET'])
@token_auth.login_required
def get_orderlists(id, period):
    appointment = Appointment.query.get_or_404(id)
    orderlists = appointment.orderlists.filter_by(period=period).all()
    lists = []
    for i in orderlists:
        name = Patient.query.get(i.patient_id).name
        dic = i.to_dict()
        dic['patient_name'] = name
        lists.append(dic)
    return jsonify(lists)

@app.route('/appointments/orderlists/<int:id>/<int:num>', methods=['GET'])
@token_auth.login_required
def get_all_orderlists(id, num):
    appointments = Appointment.query.filter_by(doctor_id=id).order_by(Appointment.appointment_date.desc()).all()[0:num]
    jsondata = {}
    jsondata['code'] = 200
    jsondata['lists'] = []
    if not appointments:
        return jsonify({})
    for i in appointments:
        dict = []
        for j in i.orderlists:
            dictiontary = j.to_dict()
            dictiontary['date'] = i.appointment_date
            dictiontary['cost'] = i.cost
            dict.append(dictiontary)
        jsondata['lists'].append(dict)
    return jsonify(jsondata)