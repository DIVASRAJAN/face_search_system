import chromadb
from chromadb.config import Settings
import os
import pandas as pd
from datetime import datetime
from backend.logger import setup_logger

logger = setup_logger("backend.db")

# Initialize ChromaDB client
CHROMA_DATA_PATH = "/home/divasrajan/attendence_system/data/chromadb"
ATTENDANCE_CSV_PATH = "/home/divasrajan/attendence_system/data/attendance.csv"

client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

# Get or create the collection for face embeddings
# We use L2 distance (Euclidean) for face matching
collection = client.get_or_create_collection(
    name="user_faces",
    metadata={"hnsw:space": "l2"} 
)

def register_user_in_db(user_id: str, name: str, encoding: list):
    """
    Saves the face encoding and user metadata to ChromaDB.
    """
    logger.info(f"Registering user: {name} (ID: {user_id})")
    collection.add(
        embeddings=[encoding],
        metadatas=[{"name": name}],
        ids=[user_id]
    )
    logger.debug(f"User {user_id} added to ChromaDB collection.")

def search_user_by_face(encoding: list, threshold: float = 0.4):
    """
    Searches for the closest face in the database.
    Returns (user_id, name, distance) if found within threshold, else None.
    """
    results = collection.query(
        query_embeddings=[encoding],
        n_results=1
    )
    
    if not results['ids'] or not results['ids'][0]:
        logger.warning("No matches found in ChromaDB.")
        return None
    
    distance = results['distances'][0][0]
    user_id = results['ids'][0][0]
    name = results['metadatas'][0][0]['name']
    print("disssssttttttt",distance)
    print("threshold",threshold)
    if distance <= threshold:
        logger.info(f"Match found: {name} ({user_id}) with distance {distance:.4f}")
        return user_id, name, distance
    
    logger.info(f"Identity unknown: Nearest match {name} is at distance {distance:.4f} (Threshold: {threshold})")
    return None

def mark_attendance(user_id: str, name: str):
    """
    Logs attendance in the CSV file. Prevents duplicates for the same day.
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    # Check if file exists, if not create with header
    if not os.path.exists(ATTENDANCE_CSV_PATH):
        df = pd.DataFrame(columns=["User ID", "Name", "Date", "Time"])
        df.to_csv(ATTENDANCE_CSV_PATH, index=False)
    
    # Read existing records, ensuring User ID is read as a string
    df = pd.read_csv(ATTENDANCE_CSV_PATH, dtype={"User ID": str})
    
    # Check for duplicate today
    user_id = str(user_id)
    is_duplicate = ((df["User ID"] == user_id) & (df["Date"] == date_str)).any()
    
    if not is_duplicate:
        new_record = {"User ID": user_id, "Name": name, "Date": date_str, "Time": time_str}
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        df.to_csv(ATTENDANCE_CSV_PATH, index=False)
        logger.info(f"Attendance MARKED: {name} on {date_str} at {time_str}")
        return True, "Attendance marked successfully"
    else:
        logger.warning(f"Attendance DUPLICATE: {name} already marked today ({date_str})")
        return False, "Attendance already marked for today"

def get_attendance_records():
    """
    Returns all attendance records.
    """
    if os.path.exists(ATTENDANCE_CSV_PATH):
        return pd.read_csv(ATTENDANCE_CSV_PATH).to_dict(orient="records")
    return []
