import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import sys


MARGIN = 10 
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green

def draw_landmarks_on_image(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Draw the hand landmarks manually
        height, width, _ = annotated_image.shape
        
        # Draw connections between landmarks
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)  # Palm
        ]
        
        # Draw connections
        for connection in connections:
            start_idx = connection[0]
            end_idx = connection[1]
            
            start_point = (
                int(hand_landmarks[start_idx].x * width),
                int(hand_landmarks[start_idx].y * height)
            )
            end_point = (
                int(hand_landmarks[end_idx].x * width),
                int(hand_landmarks[end_idx].y * height)
            )
            
            cv2.line(annotated_image, start_point, end_point, (255, 255, 255), 2)
        
        # Draw landmark points
        for landmark in hand_landmarks:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            cv2.circle(annotated_image, (x, y), 5, (0, 255, 0), -1)
            cv2.circle(annotated_image, (x, y), 5, (0, 0, 0), 1)

        # Get the top left corner of the detected hand's bounding box
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # Draw handedness (left or right hand) on the image
        cv2.putText(annotated_image, f"{handedness[0].category_name}",
                    (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                    FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    return annotated_image

def processImg(imgPath, jobid):
    # STEP 2: Create a HandLandmarker object
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
    detector = vision.HandLandmarker.create_from_options(options)

    # STEP 3: Load the input image
    image = mp.Image.create_from_file(imgPath)

    # STEP 4: Detect hand landmarks
    detection_result = detector.detect(image)

    # STEP 5: Draw result
    annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)

    output_path = f'output/{jobid}.jpg'
    cv2.imwrite(output_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

    print(output_path)  



if __name__ == "__main__":
    imgPath = sys.argv[1]
    jobid   = sys.argv[2]

    result = processImg(imgPath, jobid)
    print(result)