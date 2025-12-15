import cv2
from services.qr_scanner import scan_qr
from services.user_service import get_user

z = True

def camera():
    print("Loading cascades")

    face_cascade = cv2.CascadeClassifier('utils\\haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)

    print("Camera is starting")
    global z
    while z:
        ret, img = cap.read()
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(grey, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 55), 2)
            if x:
                print(f"Face detected {int(x),int(y)}")


            roi_grey = grey[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]

        qr_result = scan_qr(img)

        if qr_result:
            user = get_user(qr_result)
            if user:
                print(f"Zeskanowano użytkownika: {user['name']} (ID: {qr_result})")
            else:
                print("cos jest nietego")

        cv2.imshow('img', img)
        
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
    cap.release()

    cv2.destroyAllWindows()