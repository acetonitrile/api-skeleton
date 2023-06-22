from src.extensions import db
from flask import jsonify
from sqlalchemy import Time


class DummyModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.String, nullable=False)

    def json(self) -> str:
        """
        :return: Serializes this object to JSON
        """
        return jsonify({'id': self.id, 'value': self.value})

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'full_name': self.full_name
        }

class WorkingHour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)
    start_hour = db.Column(Time, nullable=False)
    end_hour = db.Column(Time, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'day_of_week': self.day_of_week,
            'start_hour': self.start_hour.strftime('%H:%M:%S'),
            'end_hour': self.end_hour.strftime('%H:%M:%S')
        }

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    patient_id = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            #'id': self.id,
            'doctor_id': self.doctor_id,
            'patient_id': self.patient_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat()
        }