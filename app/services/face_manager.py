from pathlib import Path
import cv2
import numpy as np

FACES_DIR = Path("data/faces")

def save_face_image(image: np.ndarray, user_id: int, filename: str = None) -> Path:

    user_dir = FACES_DIR / f"user_{user_id}"
    user_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:

        existing_images = list(user_dir.glob("*.jpg"))
        image_number = len(existing_images) + 1
        filename = f"user_{user_id}_{image_number}.jpg"
    
    output_path = user_dir / filename

    cv2.imwrite(str(output_path), image)

    return output_path


def has_face(user_id: int) -> bool:

    user_dir = FACES_DIR / f"user_{user_id}"

    if not user_dir.exists():
        return False

    images = list(user_dir.glob("*.jpg"))
    return len(images) > 0


def get_face_path(user_id: int) -> list[Path]:

    user_dir = FACES_DIR / f"user_{user_id}"

    if not user_dir.exists():
        return []
    
    return list(user_dir.glob("*.jpg"))


def get_face_count(user_id: int) -> int:
   
    return len(get_face_images_paths(user_id))


def delete_user_faces(user_id: int) -> bool:
    
    user_dir = FACES_DIR / f"user_{user_id}"
    
    if not user_dir.exists():
        return False
    
    for image_path in user_dir.glob("*.jpg"):
        image_path.unlink()
    
    try:
        user_dir.rmdir()
    except:
        pass
    
    return True