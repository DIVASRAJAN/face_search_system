import face_recognition
import numpy as np
import cv2
from backend.logger import setup_logger

logger = setup_logger("backend.face_engine")

def extract_face_encodings(image_content: bytes):
    """
    Extracts face encodings and provides feedback on image quality/content.
    """
    nparr = np.frombuffer(image_content, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        return None, 0, "Unsupported or corrupted image format."

    # Quality Checks (Simple)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 1. Blur detection using Laplacian variance
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    is_blurry = laplacian_var < 150 # Increased threshold for stricter quality
    logger.debug(f"Blur variance: {laplacian_var:.2f} (Threshold: 150)")
    
    # 2. Brightness check
    brightness = np.mean(gray)
    is_poor_lighting = brightness < 40 or brightness > 230
    logger.debug(f"Mean brightness: {brightness:.2f} (Range: 40-230)")

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Use 'hog' for faster/more stable CPU detection
    face_locations = face_recognition.face_locations(rgb_image, model="hog")
    encodings = face_recognition.face_encodings(rgb_image, face_locations)
    
    feedback = []
    if is_blurry:
        feedback.append("Image is too blurry.")
    if is_poor_lighting:
        feedback.append("Lighting is poor.")
    
    status = "OK" if not feedback else " ".join(feedback)
    logger.info(f"Detection result: {len(face_locations)} faces, Quality: {status}")
    
    if len(face_locations) == 0:
        return [], 0, "No face detected. " + status
    
    return encodings, len(face_locations), status
