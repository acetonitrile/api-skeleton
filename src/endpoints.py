from flask import Blueprint, jsonify, request
from http import HTTPStatus
from src.extensions import db
from src.models import DummyModel
from webargs import fields
from webargs.flaskparser import use_args
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import logging

from src.models import Doctor, WorkingTime, Appointment

import datetime

from datetime import datetime as dt

logging.basicConfig(level=logging.DEBUG)
home = Blueprint('/', __name__)


# Helpful documentation:
# https://webargs.readthedocs.io/en/latest/framework_support.html
# https://flask.palletsprojects.com/en/2.0.x/quickstart/#variable-rules


@home.route('/')
def index():
    return {'data': 'OK'}


@home.route('/dummy_model/<id_>', methods=['GET'])
def dummy_model(id_):
    record = DummyModel.query.filter_by(id=id_).first()
    if record is not None:
        return record.json()
    else:
        return jsonify(None), HTTPStatus.NOT_FOUND


@home.route('/dummy_model', methods=['POST'])
@use_args({'value': fields.String()})
def dummy_model_create(args):
    new_record = DummyModel(value=args.get('value'))
    db.session.add(new_record)
    db.session.commit()
    return new_record.json()

@home.route('/create', methods=['POST'])
def create_appointment():
    data = request.get_json()

    doctor_id = data.get('doctor_id')
    patient_id = data.get('patient_id')
    start_time = dt.fromisoformat(data.get('start_time'))
    end_time = dt.fromisoformat(data.get('end_time'))

    '''table_name = Doctor.__tablename__
    table_state = []
    inspector = inspect(db.engine)
    columns = inspector.get_columns(table_name)
    
    for row in db.session.query(Doctor).all():
        row_state = {column['name']: getattr(row, column['name']) for column in columns}
        table_state.append(row_state)
    
    logging.info(table_state)
    return jsonify(table_state)'''
    doctor = Doctor.query.get(doctor_id)
    if doctor is None:
        return jsonify(error="Doctor not found"), 404

    # Check if the time is within the doctor's working hours
    working_time = WorkingTime.query.filter_by(doctor_id=doctor_id, day_of_week=start_time.strftime('%A')).first()
    if working_time is None or not (working_time.start_time <= start_time.time() < working_time.end_time and
                                     working_time.start_time < end_time.time() <= working_time.end_time):
        return jsonify(error="Outside of working hours"), 409

    # Check for conflicting appointments
    conflicting_appointment = Appointment.query.filter_by(doctor_id=doctor_id).filter(
        (Appointment.start_time < end_time) & (Appointment.end_time > start_time)).first()
    if conflicting_appointment is not None:
        return jsonify(error="Conflicting appointment"), 409

    # Create the appointment
    appointment = Appointment(doctor_id=doctor_id, patient_id=patient_id, start_time=start_time, end_time=end_time)
    db.session.add(appointment)
    db.session.commit()

    return jsonify(id=appointment.id), 200


@home.route('/get_appointment_doc', methods=['GET'])
def get_appointments():
    doctor_id = request.args.get('doctor_id')
    start_time = dt.fromisoformat(request.args.get('start_time'))
    end_time = dt.fromisoformat(request.args.get('end_time'))

    appointments = Appointment.query.filter_by(doctor_id=doctor_id).filter(
        (Appointment.start_time >= start_time) & (Appointment.end_time <= end_time)).all()

    return jsonify(appointments=[a.serialize() for a in appointments]), 200

#assumes appointment cannot go into the next business day
#only gives appointment opening up to 3 years into the future
#This is inefficient to increment time by 1 minutes each, better to get a list of sorted intervals that the doctor is free
@home.route('/get_first_available_appointment', methods=['GET'])
def get_first_available_appointment():
    doctor_id = request.args.get('doctor_id')
    desired_duration = int(request.args.get('duration'))
    after_time = dt.fromisoformat(request.args.get('after_time'))

    current_time = after_time

    # Check if the doctor exists
    doctor = Doctor.query.get(doctor_id)
    if doctor is None:
        return jsonify(error="Doctor not found"), 404

    #Prevents infinite loop
    while current_time - after_time < datetime.timedelta(days=3 * 366):
        # Get the working hours for the current day
        working_time = WorkingTime.query.filter_by(doctor_id=doctor_id, day_of_week=current_time.strftime('%A')).first()
        if working_time is None:
            # If the doctor doesn't work this day, increment to the next day and continue
            current_time = (current_time + datetime.timedelta(days=1)).replace(hour=0, minute=0)
            continue
        
        # Check if the current time is outside of the doctor's working hours for this day
        if not (working_time.start_time <= current_time.time() < working_time.end_time):
            # If outside of working hours, increment to the next day and continue
            current_time = (current_time + datetime.timedelta(days=1)).replace(hour=working_time.start_time.hour, minute=working_time.start_time.minute)
            continue
        
        # Check for conflicting appointments and if appointment fits within working hours
        end_time = current_time + datetime.timedelta(minutes=desired_duration)

        end_of_working_time = datetime.datetime.combine(current_time.date(), working_time.end_time)

        if end_time > end_of_working_time: 
            # If the end_time is later than the end of working hours, 
            # then increment to the start of the next working day and continue
            current_time = (current_time + datetime.timedelta(days=1)).replace(hour=working_time.start_time.hour, minute=working_time.start_time.minute)
            continue

        conflicting_appointment = Appointment.query.filter_by(doctor_id=doctor_id).filter(
            (Appointment.start_time < end_time) & (Appointment.end_time > current_time)).first()

        if conflicting_appointment is None:
            # No conflicting appointments and appointment fits within working hours, 
            # this slot is available
            return jsonify(start_time=current_time.isoformat(), end_time=end_time.isoformat()), 200

        # Increment the current time by the minimum appointment duration
        current_time += datetime.timedelta(minutes=1)


    return jsonify(error="No free appointments for next 3 years"), 409
