import json
from pathlib import Path
import cv2
import os
import time
USERS_FILE = Path("data/users.json")


def load_users():
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


def add_user(name: str):
    users = load_users()

    # nowe ID (max + 1)
    new_id = str(max(map(int, users.keys()), default=0) + 1)

    users[new_id] = {
        "name": name
    }

    save_users(users)

    face_cascade = cv2.CascadeClassifier('utils\\haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)
    arr = []
    os.mkdir(f"data/known_faces/{name}")
    while True:
        ret, img = cap.read()
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(grey, 1.3, 5)
        

        for (x, y, w, h) in faces:
            #cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 55), 2)
            if x:
                
                if len(arr) < 5:
                    s = img[y-15:y+h+15, x-15:x+w+15]
                    arr.append(s)
                    time.sleep(0.5)
                else:
                    for i, image in enumerate(arr):
                        cv2.imwrite(f"data/known_faces/{name}/{i}.png", image)
                    k = cv2.waitKey(5)
                    cap.release()

                    cv2.destroyAllWindows()
                    return new_id

        cv2.imshow('img', img)



def get_user(user_id: str):
    users = load_users()
    return users.get(user_id)
