from http import HTTPStatus

from datetime import datetime as dt

def test_home_api(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    # Response is binary string data because data is the raw data of the output.
    # The switch from ' to " is due to json serialization
    assert response.data == b'{"data":"OK"}\n'
    # json allows us to get back a deserialized data structure without us needing to manually do it
    assert response.json == {'data': 'OK'}


def test_dummy_model_api(client):
    response = client.post('/dummy_model', json={
        'value': 'foobar'
    })
    assert response.status_code == HTTPStatus.OK
    obj = response.json
    new_id = obj.get('id')
    response = client.get(f'/dummy_model/{new_id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json.get('value') == 'foobar'

import datetime

def test_create_appointment_api(client):
    #7/17 is a monday
    response = client.post('/create', json={
        'doctor_id': 1,
        'patient_id': 1,
        'start_time': "2023-07-17T10:00:00",
        'end_time': "2023-07-17T11:00:00"
    })
    assert response.status_code == HTTPStatus.OK
    obj = response.json
    print(obj)
    new_appointment_id = obj.get('id')

    #7/19 is a tuesday, allow patient to book multiple appointments
    response = client.post('/create', json={
        'doctor_id': 1,
        'patient_id': 1,
        'start_time': "2023-07-18T10:00:00",
        'end_time': "2023-07-18T11:30:00"
    })
    assert response.status_code == HTTPStatus.OK
    obj = response.json
    new_appointment_id = obj.get('id')
    
    #different doctor, but same patient, let's allow it for now (e.g. patient need to see both at same time0)
    response = client.post('/create', json={
        'doctor_id': 2,
        'patient_id': 1,
        'start_time': "2023-07-18T10:00:00",
        'end_time': "2023-07-18T11:00:00"
    })
    assert response.status_code == HTTPStatus.OK
    obj = response.json
    new_appointment_id = obj.get('id')


    # Try to create an overlapping appointment
    response = client.post('/create', json={
        'doctor_id': 1,
        'patient_id': 2,
        'start_time': "2023-07-18T10:30:00",
        'end_time': "2023-07-18T11:30:00"
    })
    assert response.status_code == HTTPStatus.CONFLICT  # Assuming CONFLICT status code for conflicting appointments

    # Try to create an appointment outside working hours on a day they do work
    response = client.post('/create', json={
        'doctor_id': 1,
        'patient_id': 3,
        'start_time': "2023-07-18T07:00:00",
        'end_time': "2023-07-18T08:00:00"
    })
    assert response.status_code == HTTPStatus.CONFLICT  # Assuming CONFLICT status code for conflicting appointments

    # Try to create an appointment on a non-working day, 7/22 is Sat
    response = client.post('/create', json={
        'doctor_id': 1,
        'patient_id': 3,
        'start_time': "2023-07-22T09:00:00",
        'end_time': "2023-07-22T10:00:00"
    })
    assert response.status_code == HTTPStatus.CONFLICT  # Assuming CONFLICT status code for conflicting appointments

def test_get_appointment_doc_api(client):
    #7/17 is a monday
    apt1 = {
        'doctor_id': 1,
        'patient_id': 1,
        'start_time': "2023-07-17T10:00:00",
        'end_time': "2023-07-17T11:00:00"
    }
    response = client.post('/create', json=apt1)

    #7/18 is a tuesday, allow patient to book multiple appointments
    apt2 = {
        'doctor_id': 1,
        'patient_id': 1,
        'start_time': "2023-07-18T10:00:00",
        'end_time': "2023-07-18T11:30:00"
    }
    response = client.post('/create', json=apt2)

    start_time = dt.fromisoformat("2023-07-10T09:00:00")
    end_time = (dt.now() + datetime.timedelta(days=30)).isoformat()

    response = client.get(f'/get_appointment_doc?doctor_id=1&start_time={start_time}&end_time={end_time}')
    assert response.status_code == HTTPStatus.OK

    # Test that the returned appointments are within the specified time window
    
    appointments = response.json.get('appointments')
    print('appointments booked', appointments)
    assert apt1 in appointments
    assert apt2 in appointments


    #test no appointment if daterange doesn't overlap
    start_time = dt.fromisoformat("2023-06-10T09:00:00")
    end_time = (dt.now() + datetime.timedelta(days=10)).isoformat()

    response = client.get(f'/get_appointment_doc?doctor_id=1&start_time={start_time}&end_time={end_time}')
    assert response.status_code == HTTPStatus.OK

    # Test that the returned appointments are within the specified time window
    
    appointments = response.json.get('appointments')
    assert not appointments


def test_get_appointment_doc_api(client):
    start_time = dt.fromisoformat("2023-07-10T09:00:00")
    end_time = (dt.now() + datetime.timedelta(days=1)).isoformat()

    response = client.get(f'/get_appointment_doc?doctor_id=1&start_time={start_time}&end_time={end_time}')
    assert response.status_code == HTTPStatus.OK

    # Test that the returned appointments are within the specified time window
    
    appointments = response.json.get('appointments')
    assert not appointments
        

def test_get_first_available_appointment_api(client):
    #happy path
    duration = 1
    after_time = dt.now().isoformat()
    response = client.get(f'/get_first_available_appointment?doctor_id=1&after_time={after_time}&duration={duration}')
    assert response.status_code == HTTPStatus.OK

    appointment = response.json
    print("next appointment response:", response.json)
    assert after_time <= appointment['start_time']
    assert dt.fromisoformat(appointment['end_time']) - dt.fromisoformat(appointment['start_time']) == datetime.timedelta(minutes=duration)

    #books to next biz day
    duration = 40
    #7/18 is a tuesday
    after_time = "2023-07-18T16:40:00"

    response = client.get(f'/get_first_available_appointment?doctor_id=1&after_time={after_time}&duration={duration}')
    assert response.status_code == HTTPStatus.OK

    # Test that the returned appointment is after the specified time
    appointment = response.json
    print("next appointment response:", response.json)
    assert appointment['start_time'] == "2023-07-20T00:00:00"
    assert dt.fromisoformat(appointment['end_time']) - dt.fromisoformat(appointment['start_time']) == datetime.timedelta(minutes=duration)


    # 14 hr duration, fail as no doctors work that long
    duration = 14 * 60
    response = client.get(f'/get_first_available_appointment?doctor_id=1&after_time={dt.now().isoformat()}&duration={duration}')
    print("next appointment response:", response.json)
    appointment = response.json

    assert response.status_code == HTTPStatus.CONFLICT