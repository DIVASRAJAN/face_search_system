# FacePulse Attendance System

A modern, fast, and secure face detection-based attendance system built with FastAPI, Streamlit, and ChromaDB.

## Features
- **Face Registration**: Capture face from webcam or upload an image to register a user.
- **Vector Search**: Uses ChromaDB to store 128D face embeddings and perform lightning-fast similarity comparisons.
- **Attendance Logging**: Automatically marks attendance once a day for recognized users.
- **Web Interface**: Clean and intuitive Streamlit frontend.

## Installation

### Prerequisites
- Python 3.13+
- `uv` (Fastest Python package manager)
- System libraries (CMake, GCC-C++) for building `dlib`.

### Setup
1. Clone the repository and navigate to the project directory.
2. Install dependencies:
   ```bash
   uv add fastapi uvicorn streamlit face_recognition chromadb pandas python-multipart requests opencv-python
   ```

## Running the Application

### 1. Start the Backend (FastAPI)
```bash
uv run python -m backend.main
```
The API will be available at `http://localhost:8000`.

### 2. Start the Frontend (Streamlit)
```bash
uv run streamlit run frontend/app.py
```
The UI will be available at `http://localhost:8501`.

## Project Structure
- `backend/`: FastAPI server, face engine, and database logic.
- `frontend/`: Streamlit web application.
- `data/`: Storage for face vectors (ChromaDB) and attendance CSV logs.

## Docker Support

You can run the entire system using Docker and Docker Compose. This ensures all dependencies (like `dlib` and `cmake`) are correctly installed within a containerized environment.

### Prerequisites
- Docker
- Docker Compose

### Run with Docker Compose

1. **Build and start the containers:**
   ```bash
   docker-compose up --build
   ```

2. **Access the applications:**
   - **Frontend (UI):** [http://localhost:8501](http://localhost:8501)
   - **Backend (API):** [http://localhost:8000](http://localhost:8000)

### Persistence
The system uses a Docker volume mapping for the `./data` directory. Your face registrations and attendance records will persist even if you stop or delete the containers.

