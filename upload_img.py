import requests
import os

API_URL = 'http://localhost:3000/process-image'
IMAGE_DIR = 'sample_img'
NUM_IMAGES = 10
def send_all_images():
    print(f"Starting image path submission to {API_URL}")
    for i in range(1, NUM_IMAGES + 1):
        file_name = f'img{i}.jpg'
        file_path = os.path.join(IMAGE_DIR, file_name)
        print(f"Processing: {file_path}")
        
        if os.path.exists(file_path):
            try:
                
                response =  requests.post(API_URL, json={"imgPath": file_path})
                
                if response.status_code == 202:
                    result = response.json()
                    print(f" Success: Job {result['jobId']} created")
                else:
                    print(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Request failed: {e}")
        else:
            print(f"File not found: {file_path}")
    
    print("All image paths submitted.")

if __name__ == "__main__":
    send_all_images()