import cv2
import numpy as np

# Camera settings
CAMERA_INDEX = 0
MIN_BLOCK_AREA = 1500

# Open Logitech webcam
cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    raise RuntimeError(
        "Could not open webcam. Check CAMERA_INDEX."
    )

print("Camera started. Press Q to quit.")

try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture frame.")
            break

        # Smooth image and convert to HSV
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Red wraps around the HSV hue range
        red_lower_1 = np.array([0, 120, 64])
        red_upper_1 = np.array([9, 255, 255])
        red_lower_2 = np.array([173, 120, 64])
        red_upper_2 = np.array([179, 255, 255])

        red_mask = (
            cv2.inRange(hsv, red_lower_1, red_upper_1)
            | cv2.inRange(hsv, red_lower_2, red_upper_2)
        )

        # Yellow mask
        yellow_lower = np.array([19, 100, 89])
        yellow_upper = np.array([32, 255, 255])
        yellow_mask = cv2.inRange(
            hsv, yellow_lower, yellow_upper
        )

        # Clean masks
        kernel = np.ones((5, 5), np.uint8)

        red_mask = cv2.morphologyEx(
            red_mask, cv2.MORPH_OPEN, kernel
        )
        red_mask = cv2.morphologyEx(
            red_mask, cv2.MORPH_CLOSE, kernel
        )

        yellow_mask = cv2.morphologyEx(
            yellow_mask, cv2.MORPH_OPEN, kernel
        )
        yellow_mask = cv2.morphologyEx(
            yellow_mask, cv2.MORPH_CLOSE, kernel
        )

        # Process red and yellow objects
        objects = [
            ("RED", red_mask, "Conveyor 1"),
            ("YELLOW", yellow_mask, "Conveyor 2"),
        ]

        for colour, mask, destination in objects:
            contours, _ = cv2.findContours(
                mask,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE,
            )

            for contour in contours:
                area = cv2.contourArea(contour)

                if area < MIN_BLOCK_AREA:
                    continue

                x, y, w, h = cv2.boundingRect(contour)

                # Centre of detected object in pixels
                cx = x + w // 2
                cy = y + h // 2

                cv2.rectangle(
                    frame, (x, y), (x + w, y + h),
                    (0, 255, 0), 2
                )
                cv2.drawMarker(
                    frame, (cx, cy), (0, 255, 0),
                    cv2.MARKER_CROSS, 15, 2
                )

                label = (
                    f"{colour} ({cx}, {cy})"
                )
                cv2.putText(
                    frame, label, (x, max(25, y - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 2
                )

                cv2.putText(
                    frame, f"Sort: {destination}",
                    (x, y + h + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 255), 2
                )

        cv2.imshow("UR5e - Red and Yellow Detection", frame)
        cv2.imshow("Red Mask", red_mask)
        cv2.imshow("Yellow Mask", yellow_mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Camera closed.")