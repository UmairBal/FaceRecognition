import os
import pickle
from datetime import datetime
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

from EncodeGenerator import bucket

cap = cv2.VideoCapture(0)
# Initialize Firebase
def initialize_firebase():
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://faceattendancerealtime-a6b7c-default-rtdb.firebaseio.com/",
        'storageBucket': "faceattendancerealtime-a6b7c.appspot.com"
    })

# Load known face encodings and student IDs from the encode file
def load_known_face_encodings(file_path):
    with open(file_path, 'rb') as file:
        encode_list_known_with_ids = pickle.load(file)
    encode_list_known, students_ids = encode_list_known_with_ids
    return encode_list_known, students_ids

# Capture webcam frames
def capture_frames():
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    return cap

# Load background and mode images
def load_images():
    img_background = cv2.imread('Resources/background.png')
    folder_mode_path = 'Resources/Modes'
    mode_path_list = os.listdir(folder_mode_path)
    img_mode_list = [cv2.imread(os.path.join(folder_mode_path, path)) for path in mode_path_list]
    return img_background, img_mode_list

# Recognize and identify faces in the current frame
def recognize_faces(encode_list_known, students_ids, img_background, img_mode_list, mode_type, counter, id, img_student):
    success, img = cap.read()

    img_s = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    img_s = cv2.cvtColor(img_s, cv2.COLOR_BGR2RGB)

    face_cur_frame = face_recognition.face_locations(img_s)
    encode_cur_frame = face_recognition.face_encodings(img_s, face_cur_frame)
    img_background[162:162 + 480, 55:55 + 640] = img
    img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]

    if face_cur_frame:
        for encode_face, face_loc in zip(encode_cur_frame, face_cur_frame):
            matches = face_recognition.compare_faces(encode_list_known, encode_face)
            face_distance = face_recognition.face_distance(encode_list_known, encode_face)
            match_index = np.argmin(face_distance)

            if matches[match_index]:
                y1, x2, y2, x1 = face_loc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = x1 + 55, y1 + 162, x2 - x1, y2 - y1
                img_background = cvzone.cornerRect(img_background, bbox)
                id = students_ids[match_index]
                if counter == 0:
                    cvzone.putTextRect(img_background, "loading", (275, 400))
                    cv2.imshow("Face Attendance", img_background)
                    cv2.waitKey(1)
                    counter = 1
                    mode_type = 1

        if counter != 0:
            if counter == 1:
                try:
                    student_info = db.reference(f'Students/{id}').get()
                    blob = bucket.get_blob(f'Images/{id}.jpg')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    img_student = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                    datetime_object = datetime.strptime(student_info['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                    seconds_elapsed = (datetime.now() - datetime_object).total_seconds()
                    if seconds_elapsed > 30:
                        ref = db.reference(f'Students/{id}')
                        student_info['total_attendance'] += 1
                        ref.child('total_attendance').set(student_info['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        mode_type = 3
                        counter = 0
                        img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]

                except Exception as e:
                    print("Error: ", e)

            if mode_type != 3:

                counter += 1
                if counter >= 20:
                    counter = 0
                    mode_type = 2
                    student_info = []
                    img_student = []
                    img_background[44:44 + 633, 808:808 + 414] = img_mode_list[mode_type]
    else:
        mode_type = 2
        counter = 0
    cv2.imshow("Face Attendance", img_background)
    cv2.waitKey(1)
    return mode_type, counter, id, img_student

def main():
    encode_list_known, students_ids = load_known_face_encodings('EncodeFile.p')
    cap = capture_frames()
    img_background, img_mode_list = load_images()

    mode_type = 2
    counter = 0
    id = -1
    img_student = []

    while True:
        mode_type, counter, id, img_student = recognize_faces(encode_list_known, students_ids,
                                                              img_background, img_mode_list,
                                                              mode_type, counter, id, img_student)

if __name__ == "__main__":
    main()
