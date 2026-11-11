import cv2
import numpy as np

CAMERA_INDEX = 0
CHECKERBOARD = (6, 8)  # inner corners: columns, rows
SQUARE_SIZE_MM = 20.0
MIN_BLOCK_AREA = 1200

RED_LOW_1 = np.array([0, 100, 70])
RED_HIGH_1 = np.array([10, 255, 255])
RED_LOW_2 = np.array([170, 100, 70])
RED_HIGH_2 = np.array([179, 255, 255])
YELLOW_LOW = np.array([18, 80, 80])
YELLOW_HIGH = np.array([40, 255, 255])


def detect_blocks(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    red = cv2.bitwise_or(
        cv2.inRange(hsv, RED_LOW_1, RED_HIGH_1),
        cv2.inRange(hsv, RED_LOW_2, RED_HIGH_2))
    yellow = cv2.inRange(hsv, YELLOW_LOW, YELLOW_HIGH)

    kernel = np.ones((5, 5), np.uint8)
    red = cv2.morphologyEx(red, cv2.MORPH_OPEN, kernel)
    yellow = cv2.morphologyEx(yellow, cv2.MORPH_OPEN, kernel)

    results = {}
    for name, mask in (("RED", red), ("YELLOW", yellow)):
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = [c for c in contours if cv2.contourArea(c) >= MIN_BLOCK_AREA]
        if not contours:
            continue
        contour = max(contours, key=cv2.contourArea)
        m = cv2.moments(contour)
        if m["m00"] == 0:
            continue
        cx, cy = m["m10"] / m["m00"], m["m01"] / m["m00"]
        results[name] = (int(cx), int(cy), cv2.boundingRect(contour))
    return results


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open camera index {CAMERA_INDEX}; close other camera apps "
            "or try CAMERA_INDEX = 1.")

    cols, rows = CHECKERBOARD
    board_xy_mm = np.zeros((cols * rows, 2), np.float32)
    board_xy_mm[:] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
    board_xy_mm *= SQUARE_SIZE_MM

    H = None
    print("Table mapping test. No robot connection or movement.")
    print("C = calculate mapping; R = reset; Q = quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Camera capture failed.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(
            gray, CHECKERBOARD,
            cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE)

        display = frame.copy()
        if found:
            corners = cv2.cornerSubPix(
                gray, corners, (5, 5), (-1, -1),
                (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            cv2.drawChessboardCorners(display, CHECKERBOARD, corners, True)
            cv2.putText(display, "CHECKERBOARD DETECTED", (15, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(display, "Checkerboard not detected", (15, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        blocks = detect_blocks(frame)
        if H is None:
            cv2.putText(display, "Press C to calculate table mapping", (15, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        else:
            cv2.putText(display, "PROVISIONAL table coordinates - NOT robot coordinates",
                        (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

        for name, (px, py, box) in blocks.items():
            x, y, w, h = box
            colour = (0, 0, 255) if name == "RED" else (0, 255, 255)
            cv2.rectangle(display, (x, y), (x+w, y+h), colour, 2)
            cv2.circle(display, (px, py), 5, colour, -1)
            label = f"{name} pixel ({px},{py})"
            if H is not None:
                p = np.array([[[px, py]]], dtype=np.float32)
                mapped = cv2.perspectiveTransform(p, H)[0, 0]
                label += f" | board plane ({mapped[0]:.1f}, {mapped[1]:.1f}) mm"
            cv2.putText(display, label, (x, max(20, y-8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, colour, 2)

        cv2.imshow("Table Mapping Test - No Robot Motion", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):
            ok_now, corners_now = cv2.findChessboardCorners(
                gray, CHECKERBOARD,
                cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE)
            if not ok_now:
                print("Cannot calculate: checkerboard not detected in this frame.")
                continue
            corners_now = cv2.cornerSubPix(
                gray, corners_now, (5, 5), (-1, -1),
                (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            image_xy = corners_now.reshape(-1, 2).astype(np.float32)
            H, _ = cv2.findHomography(image_xy, board_xy_mm, 0)
            if H is None:
                print("Mapping calculation failed.")
            else:
                print("\nMapping calculated.")
                print("Origin: first inner checkerboard corner; units: mm.")
                print("This is checkerboard-plane mapping, NOT robot-base coordinates.")
                print("Blocks are outside the board area; extrapolated positions may be inaccurate.")
                print("Validate at known points before any robot movement.\n")

        elif key == ord("r"):
            H = None
            print("Mapping reset.")
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
