
import cv2

CAMERA_INDEX = 0
CHECKERBOARD = (6, 8)  # Inner corners: columns, rows

cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    raise RuntimeError("Could not open camera. Check CAMERA_INDEX.")

print("Press C to detect checkerboard.")
print("Press Q to quit.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture image.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    found, corners = cv2.findChessboardCorners(
        gray,
        CHECKERBOARD,
        cv2.CALIB_CB_ADAPTIVE_THRESH
        + cv2.CALIB_CB_NORMALIZE_IMAGE
    )

    display = frame.copy()

    if found:
        cv2.cornerSubPix(
            gray,
            corners,
            (5, 5),
            (-1, -1),
            (
                cv2.TERM_CRITERIA_EPS
                + cv2.TERM_CRITERIA_MAX_ITER,
                30,
                0.001
            )
        )

        cv2.drawChessboardCorners(
            display, CHECKERBOARD, corners, found
        )

        cv2.putText(
            display,
            "CHECKERBOARD DETECTED",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )
    else:
        cv2.putText(
            display,
            "Checkerboard not detected",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    cv2.imshow("Table Calibration Test", display)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
