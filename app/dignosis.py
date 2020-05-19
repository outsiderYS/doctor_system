from flask import url_for, jsonify
from app import db, app
from app.errors import bad_request
from app.models import Doctor, Patient, OrderList, DignosisList, Appointment
from app.auth import token_auth
from flask import request

@app.route('/dignosis/<int:doctor_id>/<int:patient_id>/<int:order_id>/<date>', methods=['PUT'])
@token_auth.login_required
def creat_dignosis_list(doctor_id, patient_id, order_id, date):
    orderlist = OrderList.query.get_or_404(order_id)
    data = request.get_json() or {}
    if DignosisList.query.filter_by(orderlist_id=order_id, doctor_id=doctor_id, patient_id=patient_id).first():
        return bad_request('诊断单已存在')
    dignosis = DignosisList(doctor_id=doctor_id, patient_id=patient_id, orderlist_id=order_id, date=date)
    dignosis.from_dict(data)
    orderlist.is_finished = True
    db.session.add(dignosis)
    db.session.commit()
    return jsonify({'code': 200})

@app.route('/dignosis/<int:patient_id>', methods=['GET'])
@token_auth.login_required
def get_patient_all_dignosis(patient_id):
    lists = DignosisList.query.filter_by(patient_id=patient_id).all()
    if lists == []:
        return jsonify({})
    jsondata = []
    for i in lists:
        jsondata.append(i.to_dict())
    return jsonify(jsondata)

@app.route('/dignosis/<int:id>/<int:num>', methods=['GET'])
@token_auth.login_required
def get_all_dignosis(id, num):
    appointments = Appointment.query.filter_by(doctor_id=id).order_by(Appointment.appointment_date.desc()).all()[
                   0:num]
    jsondata = {}
    jsondata['code'] = 200
    jsondata['dignosis'] = []
    if not appointments:
        return jsonify({})
    for i in appointments:
        dict = []
        for j in i.orderlists:
            dignosis = DignosisList.query.filter_by(orderlist_id=j.id).first()
            if dignosis:
                dictionary = dignosis.to_dict()
                dict.append(dictionary)
        jsondata['dignosis'].append(dict)
    return jsonify(jsondata)