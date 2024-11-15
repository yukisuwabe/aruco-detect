import cv2
import csv
import datetime
import os
import sys
import numpy as np
from pymediainfo import MediaInfo

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
    close_ids = np.array([])

    # If markers are detected, find the one closest to the center
    if ids is not None:
        frame_center_y = gray.shape[0] // 2
        min_distance = float("inf")
        closest_id = None
        for i, corner in enumerate(corners):
            # Calculate the center of the marker
            marker_center_y = corner[0].mean(axis=0)[1]
            distance = abs(marker_center_y - frame_center_y)
            if distance < min_distance:
                min_distance = distance
                closest_id = ids[i]

        # Only keep the closest id
        close_ids = np.array([closest_id])

    # If markers are detected, draw them on the frame
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    return close_ids


def get_video_creation_date(file_path):
    try:
        media_info = MediaInfo.parse(file_path)
        for track in media_info.tracks:
            if track.track_type == "General":
                # Look for the creation date in the metadata
                creation_date = getattr(track, "encoded_date", None)
                if not creation_date:
                    creation_date = getattr(track, "tagged_date", None)

                if creation_date:
                    # Extract the datetime part from the string
                    # Example format: "UTC 2023-11-15 10:30:00"
                    try:
                        date_str = creation_date.replace(
                            "UTC", ""
                        ).strip()  # Remove UTC prefix if present and strip whitespace
                        date_str = date_str.split(".")[
                            0
                        ]  # Remove any extra characters after the datetime
                        date_obj = datetime.datetime.strptime(
                            date_str, "%Y-%m-%d %H:%M:%S"
                        )
                        # Format as "%Y%m%d%H%M%S"
                        return date_obj
                    except ValueError as ve:
                        return f"Failed to parse datetime: {ve}"

        return None  # No creation date found
    except Exception as e:
        return f"An error occurred: {e}"


# def parse_start_time_from_filename(filename):
#     # Extract the start time from the filename (assuming format like: 20241015175216_000095)
#     files = filename.split("/")
#     filename = files[len(files) - 1]
#     start_time_str = filename.split("_")[0]
#     # Convert it into a datetime object
#     return datetime.datetime.strptime(start_time_str, "%Y%m%d%H%M%S")


def main():
    # video_name = "videos/P3_videos/20241015163430_000086.MP4"  # Example filename, change to your actual file
    video = sys.argv[1]
    # for filename in os.listdir(input_folder):
    #     if filename.endswith(".MP4"):  # Assuming video files have .MP4 extension
    #         videos.append(os.path.join(input_folder, filename))

    # print(sys.argv)
    # if not os.path.exists(video_name):
    #     print("Error: Video file not found!")
    start_time = get_video_creation_date(video)
    print(start_time)

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
        # Open CSV file for writing
        fieldnames = ["timestamp", "aruco_ids"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        cap = cv2.VideoCapture(video)
        if not cap.isOpened():
            print("Error: Cannot open video source")
            return

        # Variable to track the last second and the detected IDs within that second
        last_recorded_second = -1
        ids_per_second = []

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to read frame or end of video reached.")
                break

            print("Frame shape:", frame.shape)  # Debugging frame shape

            # height, width, _ = frame.shape
            # start_col = width // 4
            # end_col = start_col + (width // 2)
            # frame = frame[:, start_col:end_col]

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
                    ids_per_second = list(ids_per_second + new_ids)

            # If a new second has started, write the previous second's data and reset
            if elapsed_seconds != last_recorded_second:
                # Write the IDs for the previous second if not the first frame
                if last_recorded_second != -1:
                    id_named = None
                    # for i in ids_per_second:
                    #     id_named.append(aruco_dict.get(i))
                    if ids_per_second:
                        most_frequent_id = max(
                            set(ids_per_second), key=ids_per_second.count
                        )
                        id_named = aruco_dict.get(most_frequent_id)
                    writer.writerow(
                        {
                            "timestamp": actual_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
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
            id_named = None
            # for i in ids_per_second:
            #     id_named.append(aruco_dict.get(i))
            if ids_per_second:
                most_frequent_id = max(set(ids_per_second), key=ids_per_second.count)
                id_named = aruco_dict.get(most_frequent_id)
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
