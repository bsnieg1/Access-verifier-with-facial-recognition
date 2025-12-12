import cv2
from services.qr_scanner import scan_qr
from services.face_verification import FaceVerification
import os


def camera():
    print("Loading cascades")

    face_cascade = cv2.CascadeClassifier('utils\\haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)

    print("Camera is starting")

    # instantiate face verifier
    verifier = FaceVerification(known_faces_dir=os.path.join('services', 'known_faces'))

    while True:
        ret, img = cap.read()
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(grey, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 55), 2)
            # if x:
            #     print(f"Face detected {int(x),int(y)}")


            roi_grey = grey[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]

        qr_result = scan_qr(img)
        
        verification_results = verifier.verify(img)
        print(verification_results)
        if verification_results:
            for result in verification_results:
                print("Face verified:", result["label"], "confidence:", result["confidence"])

        if qr_result:
            print("QR kod:", qr_result)
        
        cv2.imshow('img', img)
        
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
    cap.release()

    cv2.destroyAllWindows()