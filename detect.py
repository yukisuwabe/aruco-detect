import cv2
import csv
import datetime
import os
import sys

DICTIONARY = (
    cv2.aruco.DICT_5X5_100
)  # This is based on the dictionary you use to generate the aruco markers

aruco_dict = {0: "dresser", 2: "reachy", 3: "table", 4: "shelf", 7: "monitor"}


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


def parse_start_time_from_filename(filename):
    # Extract the start time from the filename (assuming format like: 20241015175216_000095)
    files = filename.split("/")
    filename = files[len(files) - 1]
    start_time_str = filename.split("_")[0]
    # Convert it into a datetime object
    return datetime.datetime.strptime(start_time_str, "%Y%m%d%H%M%S")


def main():
    video_name = "videos/P3_videos/20241015163430_000086.MP4"  # Example filename, change to your actual file
    videos = []
    for s in sys.argv[1:]:
        videos.append(s)

    # print(sys.argv)
    if not os.path.exists(video_name):
        print("Error: Video file not found!")
    start_time = parse_start_time_from_filename(videos[0])

    # Create the directory if it does not exist
    output_dir = "./arucoDetectCSV/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # This creates the directory

    with open(
        output_dir
        + "aruco_detection_log_"
        + start_time.strftime("%Y-%m-%d-%H-%M-%S")
        + ".csv",
        mode="w",
        newline="",
    ) as csvfile:
        for video in videos:
            cap = cv2.VideoCapture(video)
            if not cap.isOpened():
                print("Error: Cannot open video source")
                return

            # Open CSV file for writing
            fieldnames = ["timestamp", "aruco_ids"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Variable to track the last second and the detected IDs within that second
            last_recorded_second = -1
            ids_per_second = []

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to read frame or end of video reached.")
                    break

                print("Frame shape:", frame.shape)  # Debugging frame shape

                ids = detect_aruco_tags(frame)

                # Calculate the current video time in seconds
                video_time_millis = cap.get(cv2.CAP_PROP_POS_MSEC)
                elapsed_seconds = int(
                    video_time_millis // 1000
                )  # Elapsed time from video start in seconds
                actual_timestamp = start_time + datetime.timedelta(
                    seconds=elapsed_seconds
                )  # Add elapsed time to start time

                # If still in the same second, update the detected IDs for that second
                if elapsed_seconds == last_recorded_second:
                    if ids is not None:
                        new_ids = ids.flatten().tolist()
                        # Update the detected IDs for the current second, adding any new ones
                        ids_per_second = list(set(ids_per_second + new_ids))

                # If a new second has started, write the previous second's data and reset
                if elapsed_seconds != last_recorded_second:
                    # Write the IDs for the previous second if not the first frame
                    if last_recorded_second != -1:
                        id_named = []
                        for i in ids_per_second:
                            id_named.append(aruco_dict.get(i))
                        writer.writerow(
                            {
                                "timestamp": actual_timestamp.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "aruco_ids": id_named,
                            }
                        )

                    # Reset for the new second
                    last_recorded_second = elapsed_seconds
                    if ids is not None:
                        ids_per_second = ids.flatten().tolist()
                    else:
                        ids_per_second = []

                # Display the frame with detected markers
                cv2.imshow("Aruco Tag Detection", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            # Write the remaining data for the last second when the video ends
            if ids_per_second:
                id_named = []
                for i in ids_per_second:
                    id_named.append(aruco_dict.get(i))
                writer.writerow(
                    {
                        "timestamp": actual_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "aruco_ids": id_named,
                    }
                )

            cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()  # if you have continuity camera on macos, pass 1 as the argument. You can also check the order of the cameras through photo booth.
