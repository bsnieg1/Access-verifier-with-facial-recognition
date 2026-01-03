import cv2
import face_recognition
import os
import numpy as np


import cv2
import face_recognition
import os
import numpy as np
from pathlib import Path


class FaceVerification:
    def __init__(self, faces_base_dir: str = "data/faces"):
       
        self.faces_base_dir = Path(faces_base_dir)
        print(f"FaceVerification zainicjowany z folderem: {self.faces_base_dir}")

    def _load_encodings_for_user(self, user_id: int) -> list:
        
        user_dir = self.faces_base_dir / f"user_{user_id}"
        
        if not user_dir.exists():
            print(f"Folder {user_dir} nie istnieje")
            return []
        
        encodings = []
        
        for image_file in user_dir.glob("*.jpg"):
            try:
                image = face_recognition.load_image_file(str(image_file))
                image_encodings = face_recognition.face_encodings(image)
                
                if image_encodings:
                    encodings.append(image_encodings[0])
                    print(f"Załadowano encoding z {image_file.name}")
                else:
                    print(f"Nie wykryto twarzy w {image_file.name}")
                    
            except Exception as e:
                print(f" Błąd ładowania {image_file.name}: {e}")
        
        print(f"Załadowano {len(encodings)} encodingów dla user_{user_id}")
        return encodings

    def verify_for_user(self, frame, user_id: int, threshold: float = 0.6) -> dict:
        
        known_encodings = self._load_encodings_for_user(user_id)
        
        if not known_encodings:
            return {
                "match": False,
                "confidence": 0.0,
                "bbox": None,
                "error": f"Brak zdjęć dla user_{user_id}"
            }
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb)
        face_encodings = face_recognition.face_encodings(rgb, face_locations)
        
        if not face_encodings:
            return {
                "match": False,
                "confidence": 0.0,
                "bbox": None,
                "error": "Nie wykryto twarzy na zdjęciu"
            }
        
        test_encoding = face_encodings[0]
        bbox = face_locations[0]
        
        face_distances = face_recognition.face_distance(known_encodings, test_encoding)
        
        if len(face_distances) == 0:
            return {
                "match": False,
                "confidence": 0.0,
                "bbox": bbox,
                "error": "Brak encodingów do porównania"
            }
        
        best_distance = np.min(face_distances)
        confidence = 1 - best_distance
        
        match = confidence >= threshold
        
        print(f"Weryfikacja user_{user_id}: confidence={confidence:.3f}, match={match}")
        print(f"Best distance: {best_distance:.3f}")
        print(f"Confidence: {confidence:.3f}")
        print(f"Threshold: {threshold}")
        print(f"Match: {match}")
        
        return {
            "match": match,
            "confidence": float(confidence),
            "bbox": bbox,
            "user_id": user_id
        }

# class FaceVerification:
#     def __init__(self, known_faces_dir):

        
#         self.known_face_encodings = []
#         self.known_face_labels = []

#         print("Loading known faces...")
#         self._load_known_faces(known_faces_dir)
#         print(f"Loaded {len(self.known_face_encodings)} face encodings.")

#     def _load_known_faces(self, directory):
#         for label in os.listdir(directory):
#             person_dir = os.path.join(directory, label)

#             if not os.path.isdir(person_dir):
#                 continue

#             for filename in os.listdir(person_dir):
#                 filepath = os.path.join(person_dir, filename)
#                 image = face_recognition.load_image_file(filepath)

#                 encodings = face_recognition.face_encodings(image)
#                 if encodings:
#                     self.known_face_encodings.append(encodings[0])
#                     self.known_face_labels.append(label)
                

        

#     def verify(self, frame):
#         """
#         frame: BGR image from cv2
#         returns: dict or None
#         """
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         face_locations = face_recognition.face_locations(rgb)
#         face_encodings = face_recognition.face_encodings(rgb, face_locations)

#         results = []

#         for encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
#             matches = face_recognition.compare_faces(self.known_face_encodings, encoding)
#             face_distances = face_recognition.face_distance(self.known_face_encodings, encoding)

#             if len(face_distances) == 0:
#                 continue

#             best_match_index = np.argmin(face_distances)

#             if matches[best_match_index]:
#                 label = self.known_face_labels[best_match_index]
#                 confidence = 1 - face_distances[best_match_index]
#                 results.append({
#                     "label": label,
#                     "confidence": float(confidence),
#                     "bbox": (top, right, bottom, left)
#                 })
#             else:
#                 results.append({
#                     "label": "unknown",
#                     "confidence": 0.0,
#                     "bbox": (top, right, bottom, left)
#                 })

#         return results if results else None
