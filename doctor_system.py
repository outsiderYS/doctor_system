from app import app, db
from app.models import Doctor, Patient, Appointment, Hospital, OrderList, DignosisList, Bill, DoctorPatient

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Doctor': Doctor, 'Patient': Patient, 'Appointment': Appointment, 'Hospital': Hospital,
            'OrderList': OrderList, 'DignosisList': DignosisList, 'Bill': Bill, 'DoctorPatient': DoctorPatient}
