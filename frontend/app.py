import streamlit as st
import requests
import pandas as pd
from io import BytesIO

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="FacePulse - Attendance System",
    page_icon="👤",
    layout="wide"
)

# Custom CSS for a premium look
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .title-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "User Registration", "Mark Attendance", "View Records"])

    if page == "Home":
        st.markdown('<div class="title-container"><h1>Welcome to FacePulse</h1></div>', unsafe_allow_html=True)
        st.write("""
        ### Smart Face Recognition Attendance System
        This system allows you to:
        * **Register** users with their face encoding.
        * **Recognize** users via webcam or image upload.
        * **Mark Attendance** automatically with timestamp and daily validation.
        * **Export** logs to CSV or view them in real-time.
        """)
        st.image("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80", caption="Secure & Automated")

    elif page == "User Registration":
        st.header("👤 New User Registration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input("Unique ID (e.g., EMP001)")
            user_name = st.text_input("Full Name")
            source = st.radio("Image Source", ["Webcam", "Upload"])
            
            if source == "Webcam":
                image_file = st.camera_input("Capture Face")
            else:
                image_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])
        
        with col2:
            if image_file:
                st.write("### Preview")
                st.image(image_file, use_container_width=True)
                
                if st.button("Register User", type="primary"):
                    if not user_id or not user_name:
                        st.error("Please provide both Name and ID.")
                    else:
                        files = {"file": (image_file.name, image_file.getvalue())}
                        data = {"user_id": user_id, "name": user_name}
                        
                        with st.spinner("Processing..."):
                            try:
                                response = requests.post(f"{API_URL}/register", data=data, files=files)
                                if response.status_code == 200:
                                    st.success(response.json()["message"])
                                else:
                                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"Could not connect to backend: {e}")
            else:
                st.info("Please capture or upload an image to continue.")

    elif page == "Mark Attendance":
        st.header("📸 Mark Your Attendance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            source = st.radio("Image Source", ["Webcam", "Upload"])
            if source == "Webcam":
                image_file = st.camera_input("Smile for the camera!")
            else:
                image_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])
        
        with col2:
            if image_file:
                st.write("### Preview")
                st.image(image_file, use_container_width=True)
                
                if st.button("Verify & Mark", type="primary"):
                    files = {"file": (image_file.name, image_file.getvalue())}
                    
                    with st.spinner("Recognizing..."):
                        try:
                            response = requests.post(f"{API_URL}/recognize_and_mark", files=files)
                            if response.status_code == 200:
                                results = response.json().get("results", [])
                                if not results:
                                    st.warning("No faces processed.")
                                for res in results:
                                    if res["status"] == "Recognized":
                                        st.success(f"Welcome, **{res['name']}**! Attendance marked successfully.")
                                    elif res["status"] == "Duplicate":
                                        st.warning(f"Hello **{res['name']}**, your attendance is **already marked** for today.")
                                    else:
                                        st.error("🕵️ **Unknown Person Detected**. Please ensure you are registered.")
                            else:
                                st.error(f"Error: {response.json().get('detail', 'Failed to process image')}")
                        except Exception as e:
                            st.error(f"Could not connect to backend: {e}")
            else:
                st.info("Please capture or upload an image to mark attendance.")

    elif page == "View Records":
        st.header("📋 Attendance Logs")
        
        if st.button("Refresh Logs"):
            response = requests.get(f"{API_URL}/attendance")
            if response.status_code == 200:
                records = response.json()["records"]
                if records:
                    df = pd.DataFrame(records)
                    st.dataframe(df, use_container_width=True)
                    
                    # CSV Download
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Export to CSV",
                        data=csv,
                        file_name='attendance_report.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("No attendance records found yet.")
            else:
                st.error("Could not fetch records.")

if __name__ == "__main__":
    main()
