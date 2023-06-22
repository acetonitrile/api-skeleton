from src.extensions import db
from flask import jsonify
from sqlalchemy import Enum, Time
import enum


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'full_name': self.full_name
        }


class DayOfWeekEnum(enum.Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    Sunday = "Sunday"



class WorkingTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    day_of_week = db.Column(Enum(DayOfWeekEnum), nullable=False)
    start_time = db.Column(Time, nullable=False)
    end_time = db.Column(Time, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'day_of_week': self.day_of_week.value,
            'start_time': self.start_time.strftime('%H:%M:%S'),
            'end_time': self.end_time.strftime('%H:%M:%S')
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