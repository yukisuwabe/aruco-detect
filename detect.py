import cv2
import csv
import time
import datetime

DICTIONARY = cv2.aruco.DICT_5X5_100  # this is based on the dictionary you use to generate the aruco markers


def detect_aruco_tags(frame):
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Define the dictionary of ArUco markers
    aruco_dict = cv2.aruco.getPredefinedDictionary(DICTIONARY)
    parameters = cv2.aruco.DetectorParameters()

    # Create ArUco detector
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # Detect ArUco markers in the frame
    corners, ids, rejectedImgPoints = detector.detectMarkers(gray)

    # If markers are detected, draw them on the frame
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    return ids

def main(video_source=0):
    video_name = "./tag_arduino.MP4"
    cap = cv2.VideoCapture(video_name)
    start = time.time()

     # Open CSV file for writing
    with open('./arucoDetectCSV/aruco_detection_log' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-&S") + '.csv', mode='w', newline='') as csvfile:
        fieldnames = ['timestamp', 'aruco_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            ids = detect_aruco_tags(frame)

            # If markers are detected, write to CSV
            if ids is not None:
            # for aruco_id in ids.flatten():
                timestamp = time.time() - start  # Get the current timestamp
                writer.writerow({'timestamp': timestamp, 'aruco_id': ids.flatten()})

            cv2.imshow('Aruco Tag Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() # if you have continuity camera on macos, pass 1 as the argument. You can also check the order of the cameras through photo booth.
