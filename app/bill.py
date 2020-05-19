from flask import url_for, jsonify
from app import db, app
from app.errors import bad_request
from app.models import Bill, Appointment
from app.auth import token_auth
from flask import request

@app.route('/bills/<int:id>', methods=['GET'])
@token_auth.login_required
def get_bill(id):
    bills = Bill.query.filter_by(doctor_id=id).all()
    jsondata = []
    for i in bills:
        jsondata.append(i.to_dict())
    jsondata['code'] = 200
    return jsonify(jsondata)

@app.route('/bills/<int:doctor_id>/<int:patient_id>/<int:orderlist_id>', methods=['PUT'])
@token_auth.login_required
def put_bill(doctor_id, patient_id, orderlist_id):
    data = request.get_json() or {}
    bill = Bill(doctor_id=doctor_id, patient_id=patient_id, orderlist_id=orderlist_id)
    bill.from_dict(data)
    db.session.add(bill)
    db.session.commit()
    return jsonify({'code': 200})

@app.route('/bills/<int:doctor_id>/<int:num>', methods=['GET'])
@token_auth.login_required
def get_all_bills(doctor_id, num):
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.appointment_date.desc()).all()[0:num]
    jsondata = {}
    jsondata['code'] = 200
    jsondata['bills'] = []
    if not appointments:
        return jsonify({})
    for i in appointments:
        dict = []
        for j in i.orderlists:
            bill = Bill.query.filter_by(orderlist_id=j.id).first()
            if bill:
                dictionary = bill.to_dict()
                dictionary['date'] = i.appointment_date
                dict.append(dictionary)
        jsondata['bills'].append(dict)
    return jsonify(jsondata)