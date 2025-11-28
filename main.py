import streamlit as st
from PIL import Image
import requests
import time
from io import BytesIO

st.set_page_config(page_title="detect Hand", )

API_URL = "http://localhost:3000"

st.title("Detect Hand")
st.write("Upload an image to detect hand landmarks")

def convert_image_to_bytes(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    original_image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original")
        st.image(original_image, )
    
    with col2:
        st.subheader("Processed")
        if st.session_state.processed_image:
            st.image(st.session_state.processed_image, )
            btn = st.download_button(
                label="Download Image",
                data=convert_image_to_bytes(st.session_state.processed_image),
                file_name="hand_detected.png",
                mime="image/png"
            )
        else:
            st.info("Click 'Process Image' to detect hands")
    
    if st.button("Process Image", disabled=st.session_state.processing):
        st.session_state.processing = True
        st.session_state.processed_image = None
        
        try:
            uploaded_file.seek(0)
            files = {"image": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            
            with st.spinner("Uploading..."):
                response = requests.post(f"{API_URL}/process-image", files=files, timeout=10)
            
            if response.status_code == 202:
                job_id = response.json()["jobId"]
                st.success(f"Job ID: {job_id}")
                
                progress = st.progress(0)
                status_text = st.empty()
                
                for attempt in range(60):
                    status_text.text(f"Processing... {attempt + 1}s")
                    progress.progress((attempt + 1) / 60)
                    
                    result_response = requests.get(f"{API_URL}/result/{job_id}", timeout=5)
                    
                    if result_response.status_code == 200:
                        from io import BytesIO
                        processed_image = Image.open(BytesIO(result_response.content))
                        st.session_state.processed_image = processed_image
                        status_text.text("✅ Complete!")
                        progress.progress(1.0)
                        st.session_state.processing = False
                        st.rerun()
                        break
                    elif result_response.status_code == 500:
                        st.error("Processing failed")
                        break
                    
                    time.sleep(1)
                
                st.session_state.processing = False
            else:
                st.error(f"Upload failed: {response.text}")
                st.session_state.processing = False
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API. Make sure it's running on localhost:3000")
            st.session_state.processing = False
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.processing = False
else:
    st.info("Upload an image to get started")