import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-a6b7c-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    '4202':
        {
            'name': 'Bill Gates',
            'major': 'CS',
            'starting_year': 2019,
            'total_attendance': 6,
            'standing': "G",
            'year': 4,
            'last_attendance_time': "2023-7-10 12:21:00"
        },
    '4204':
        {
            'name': 'Elon Musk',
            'majors': 'AI',
            'starting_year': 2021,
            'total_attendance': 4,
            'standing': "B",
            'year': 2,
            'last_attendance_time': "2023-7-8 12:21:00"
        },
    # '4206':
    #     {
    #         'name': 'Nicola Tesla',
    #         'majors': 'EE',
    #         'starting_year': 2019,
    #         'total_attendance': 10,
    #         'standing': "G",
    #         'year': 4,
    #         'last_attendance_time': "2023-7-9 12:21:00"
    #     },
    '4260':
        {
            'name': 'Umair Azeem',
            'majors': 'SE',
            'starting_year': 2020,
            'total_attendance': 7,
            'standing': "G",
            'year': 3,
            'last_attendance_time': "2023-7-10 12:21:00"
        }
}

for key, value in data.items():
    ref.child(key).set(value)
