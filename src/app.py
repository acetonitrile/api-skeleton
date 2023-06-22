from flask import Flask
from src.extensions import db
from src.endpoints import home
from src.models import Doctor, WorkingHour, Appointment
import datetime


def initialize_db():
    # Check if the doctors table is empty. If it is, populate the database.
    if Doctor.query.first() is None:
        # Create doctors
        doctor1 = Doctor(id=1, full_name="Doctor One")
        db.session.add(doctor1)

        doctor2 = Doctor(id=2, full_name="Doctor Two")
        db.session.add(doctor2)

        # Create working hours
        working_hours1_1 = WorkingHour(doctor_id=1, day_of_week="Monday", start_hour=datetime.time(9, 0, 0), end_hour=datetime.time(17, 0, 0))
        db.session.add(working_hours1_1)

        working_hours1_2 = WorkingHour(doctor_id=1, day_of_week="Tuesday", start_hour=datetime.time(9, 0, 0), end_hour=datetime.time(17, 0, 0))
        db.session.add(working_hours1_2)

        working_hours1_3 = WorkingHour(doctor_id=1, day_of_week="Thursday", start_hour=datetime.time(0, 0, 0), end_hour=datetime.time(8, 0, 0))
        db.session.add(working_hours1_3)

        working_hours2_1 = WorkingHour(doctor_id=2, day_of_week="Monday", start_hour=datetime.time(9, 0, 0), end_hour=datetime.time(17, 0, 0))
        db.session.add(working_hours2_1)
        working_hours2_2 = WorkingHour(doctor_id=2, day_of_week="Tuesday", start_hour=datetime.time(9, 0, 0), end_hour=datetime.time(17, 0, 0))
        db.session.add(working_hours2_2)

        # Create appointments
        appointment1 = Appointment(id=1, doctor_id=1, patient_id=1, start_time=datetime.datetime(2023, 6, 21, 10, 0, 0), end_time=datetime.datetime(2023, 6, 21, 11, 0, 0))
        db.session.add(appointment1)

        db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.init_app(app)
    # We are doing a create all here to set up all the tables. Because we are using an in memory sqllite db, each
    # restart wipes the db clean, but does have the advantage of not having to worry about schema migrations.
    with app.app_context():
        db.create_all()
        initialize_db()
    app.register_blueprint(home)
    return app
