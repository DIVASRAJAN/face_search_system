from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List
import uvicorn
import traceback

from backend.face_engine import extract_face_encodings
from backend.db import register_user_in_db, search_user_by_face, mark_attendance, get_attendance_records
from backend.logger import setup_logger

logger = setup_logger("backend.main")

app = FastAPI(title="Face Attendance System API")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.post("/register")
async def register(
    user_id: str = Form(...),
    user_name: str = Form(...),
    file: UploadFile = File(...)
):
    logger.info(f"--- Registration Request Started: {user_name} ---")
    try:
        content = await file.read()
        encodings, count, status = extract_face_encodings(content)
        
        logger.debug(f"Face count: {count}, Quality Status: {status}")
        
        if count == 0:
            raise HTTPException(status_code=400, detail=status)
        if count > 1:
            raise HTTPException(status_code=400, detail=f"Multiple faces ({count}) detected. Please upload a clear photo of one person.")
        
        # Save to database
        register_user_in_db(user_id, user_name, encodings[0].tolist())
        return {"message": f"User {user_name} registered successfully.", "quality_feedback": status}
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recognize_and_mark")
async def recognize_and_mark(file: UploadFile = File(...)):
    logger.info("--- Recognition Request Started ---")
    try:
        content = await file.read()
        encodings, count, status = extract_face_encodings(content)
        logger.debug(f"Extraction result - Count: {count}, Status: {status}")
        
        if count == 0:
            return JSONResponse(status_code=400, content={"detail": status})
        
        if count > 1:
            return JSONResponse(status_code=400, content={"detail": f"Multiple faces ({count}) detected. Please ensure only one person is in the frame."})
        
        results = []
        for encoding in encodings:
            match = search_user_by_face(encoding.tolist())
            if match:
                u_id, u_name, dist = match
                success, msg = mark_attendance(u_id, u_name)
                results.append({
                    "user_id": u_id,
                    "name": u_name,
                    "distance": dist,
                    "status": "Recognized" if success else "Duplicate",
                    "attendance_marked": success,
                    "attendance_msg": msg,
                    "quality_feedback": status
                })
            else:
                results.append({
                    "name": "Unknown",
                    "status": "Not Recognized",
                    "quality_feedback": status
                })
        
        return {"results": results}
    
    except Exception as e:
        logger.error(f"Error in recognize_and_mark: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/attendance")
async def get_attendance():
    records = get_attendance_records()
    return {"records": records}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
