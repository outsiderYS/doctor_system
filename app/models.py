from flask import url_for
from app import db
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
import base64
import os
from sqlalchemy.sql import func

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    address = db.Column(db.String(64))
    introduction = db.Column(db.String(128))
    doctors = db.relationship('Doctor', backref='location', lazy='dynamic')

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    join_time = db.Column(db.DateTime, index=True, default=datetime.now)
    age = db.Column(db.Integer)
    sex = db.Column(db.String(32))
    introduction = db.Column(db.String(256))
    notice = db.Column(db.String(128))
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    appointments = db.relationship('Appointment', backref='owner', lazy='dynamic')
    dignosislists = db.relationship('DignosisList', backref='creater', lazy='dynamic')
    bills = db.relationship('Bill', backref='get', lazy='dynamic')
    collections = db.relationship('DoctorPatient', backref='collection', lazy='dynamic')
    im_token = db.Column(db.String(64))

    def __repr__(self):
        return '<Doctor {}>'.format(self.name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'hospital': self.location.name,
            'age': self.age,
            'sex': self.sex,
            'introduction': self.introduction,
            'notice': self.notice
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'name', 'age', 'sex', 'introduction', 'notice']:
            if field in data:
                setattr(self, field, data[field])
        if 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=36000):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            self.token_expiration = now + timedelta(seconds=expires_in)
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        doctor = Doctor.query.filter_by(token=token).first()
        if doctor is None or doctor.token_expiration < datetime.utcnow():
            return None
        return doctor

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_date = db.Column(db.String(32), index=True)
    am_appointment = db.Column(db.Integer)
    am_number = db.Column(db.Integer, default=0)
    pm_appointment = db.Column(db.Integer)
    pm_number = db.Column(db.Integer, default=0)
    cost = db.Column(db.Float)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    orderlists = db.relationship('OrderList', backref='owner', lazy='dynamic')

    def to_dict(self):
        data = {
            'code': 200,
            'id': self.id,
            'appointment_date': self.appointment_date,
            'am_appointment': self.am_appointment,
            'am_number': self.am_number,
            'pm_appointment': self.pm_appointment,
            'pm_number': self.pm_number,
            'doctor_id': self.doctor_id,
            'cost': self.cost
        }
        return data

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    age = db.Column(db.Integer)
    sex = db.Column(db.String(32))
    orderlists = db.relationship('OrderList', backref='orderer', lazy='dynamic')
    dignosislists = db.relationship('DignosisList', backref='patient', lazy='dynamic')
    bills = db.relationship('Bill', backref='offer', lazy='dynamic')
    collections = db.relationship('DoctorPatient', backref='collected', lazy='dynamic')
    userid = db.Column(db.String(32))

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'sex': self.sex
        }
        return data

class OrderList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_date = db.Column(db.DateTime, index=True, default=datetime.now)
    type = db.Column(db.String(32))
    is_finished = db.Column(db.Boolean, default=False)
    period = db.Column(db.String(32))
    rank = db.Column(db.Integer)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient_name = db.Column(db.String(32))
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    dignosislist = db.relationship('DignosisList', backref='owner', lazy='dynamic')
    bill = db.relationship('Bill', backref='belong', lazy='dynamic')

    def to_dict(self):
        data = {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient_name,
            'appointment_date': self.appointment_date,
            'type': self.type,
            'is_finished': self.is_finished,
            'period': self.period,
            'rank': self.rank
        }
        return data

    def finish_list(self):
        self.is_finished = True

class DignosisList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, index=True, default=datetime.now)
    date = db.Column(db.String(32))
    symptom = db.Column(db.String(256))
    dignosis = db.Column(db.String(64))
    prescription = db.Column(db.String(256))
    advice = db.Column(db.String(64))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient_name = db.Column(db.String(32))
    orderlist_id = db.Column(db.Integer, db.ForeignKey('order_list.id'))

    def to_dict(self):
        data = {
            'id': self.id,
            'create_date': self.create_date,
            'date': self.date,
            'symptom': self.symptom,
            'dignosis': self.dignosis,
            'prescription': self.prescription,
            'advice': self.advice,
            'doctor_id': self.doctor_id,
            'patient_id': self.patient_id,
            'patient_name': self.patient_name,
            'orderlist_id': self.orderlist_id
        }
        return data

    def from_dict(self, data):
        for field in ['symptom', 'dignosis', 'prescription', 'advice', 'patient_name']:
            if field in data:
                setattr(self, field, data[field])

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, index=True, default=datetime.now)
    bill_detail = db.Column(db.String(256))
    bill_amount = db.Column(db.String(32))
    is_paid = db.Column(db.Boolean, default=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient_name = db.Column(db.String(32))
    orderlist_id = db.Column(db.Integer, db.ForeignKey('order_list.id'))

    def to_dict(self):
        data = {
            'id': self.id,
            'create_date': self.create_date,
            'bill_detail': self.bill_detail,
            'bill_amount': self.bill_amount,
            'doctor_id': self.doctor_id,
            'patient_id': self.patient_id,
            'patient_name': self.patient_name,
            'orderlist_id': self.orderlist_id,
            'is_paid': self.is_paid
        }
        return data

    def from_dict(self, data):
        for field in ['bill_detail', 'bill_amount', 'patient_name']:
            if field in data:
                setattr(self, field, data[field])

class DoctorPatient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    date = db.Column(db.String(32))