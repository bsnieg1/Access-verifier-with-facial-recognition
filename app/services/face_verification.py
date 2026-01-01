import cv2
import face_recognition
import os
import numpy as np


class FaceVerification:
    def __init__(self, known_faces_dir):

        
        self.known_face_encodings = []
        self.known_face_labels = []

        print("Loading known faces...")
        self._load_known_faces(known_faces_dir)
        print(f"Loaded {len(self.known_face_encodings)} face encodings.")

    def _load_known_faces(self, directory):
        for label in os.listdir(directory):
            person_dir = os.path.join(directory, label)

            if not os.path.isdir(person_dir):
                continue

            for filename in os.listdir(person_dir):
                filepath = os.path.join(person_dir, filename)
                image = face_recognition.load_image_file(filepath)

                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_labels.append(label)
                

        

    def verify(self, frame):
        """
        frame: BGR image from cv2
        returns: dict or None
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb)
        face_encodings = face_recognition.face_encodings(rgb, face_locations)

        results = []

        for encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(self.known_face_encodings, encoding)
            face_distances = face_recognition.face_distance(self.known_face_encodings, encoding)

            if len(face_distances) == 0:
                continue

            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                label = self.known_face_labels[best_match_index]
                confidence = 1 - face_distances[best_match_index]
                results.append({
                    "label": label,
                    "confidence": float(confidence),
                    "bbox": (top, right, bottom, left)
                })
            else:
                results.append({
                    "label": "unknown",
                    "confidence": 0.0,
                    "bbox": (top, right, bottom, left)
                })

        return results if results else None
