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

CRITERIA = (
    cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER,
    30,
    0.001,
)


def detect_checkerboard(gray):
    flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
    found, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, flags)
    if not found:
        return False, None

    corners = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), CRITERIA)
    return True, corners


def detect_blocks(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    red = cv2.bitwise_or(
        cv2.inRange(hsv, RED_LOW_1, RED_HIGH_1),
        cv2.inRange(hsv, RED_LOW_2, RED_HIGH_2),
    )
    yellow = cv2.inRange(hsv, YELLOW_LOW, YELLOW_HIGH)

    kernel = np.ones((5, 5), np.uint8)
    red = cv2.morphologyEx(red, cv2.MORPH_OPEN, kernel)
    yellow = cv2.morphologyEx(yellow, cv2.MORPH_OPEN, kernel)

    results = {}
    for name, mask in (("RED", red), ("YELLOW", yellow)):
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        contours = [c for c in contours if cv2.contourArea(c) >= MIN_BLOCK_AREA]
        if not contours:
            continue

        contour = max(contours, key=cv2.contourArea)
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            continue

        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        results[name] = (cx, cy, cv2.boundingRect(contour))

    return results


def make_board_coordinates():
    cols, rows = CHECKERBOARD
    board_xy_mm = np.zeros((cols * rows, 2), dtype=np.float32)
    board_xy_mm[:] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
    board_xy_mm *= SQUARE_SIZE_MM
    return board_xy_mm


def fit_mapping(image_corners):
    """Fit image pixels -> ideal checkerboard-plane millimetres."""
    image_xy = image_corners.reshape(-1, 2).astype(np.float32)
    board_xy_mm = make_board_coordinates()

    H, inliers = cv2.findHomography(image_xy, board_xy_mm, 0)
    if H is None or not np.isfinite(H).all():
        return None, None, None

    predicted = cv2.perspectiveTransform(image_xy.reshape(-1, 1, 2), H).reshape(-1, 2)
    errors = np.linalg.norm(predicted - board_xy_mm, axis=1)
    rms = float(np.sqrt(np.mean(errors ** 2)))
    max_error = float(np.max(errors))
    return H, rms, max_error


def point_outside_distance_px(point, polygon):
    """Distance from point to checkerboard convex hull; 0 if inside."""
    signed_distance = cv2.pointPolygonTest(
        polygon.astype(np.float32), (float(point[0]), float(point[1])), True
    )
    return max(0.0, -float(signed_distance))


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open camera index {CAMERA_INDEX}; close other camera apps "
            "or try CAMERA_INDEX = 1."
        )

    H = None
    board_hull = None
    rms_error = None
    max_error = None

    print("Table mapping validation — NO robot connection or movement.")
    print("C = calculate mapping and diagnostics; R = reset; Q = quit.")
    print("Mapping origin is the first detected INNER checkerboard corner.")
    print("Coordinates are checkerboard-plane mm, NOT robot-base coordinates.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Camera capture failed.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = detect_checkerboard(gray)
        display = frame.copy()

        if found:
            cv2.drawChessboardCorners(display, CHECKERBOARD, corners, True)
            cv2.putText(
                display, "CHECKERBOARD DETECTED", (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
            )
        else:
            cv2.putText(
                display, "Checkerboard not detected", (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
            )

        blocks = detect_blocks(frame)

        if H is None:
            status = "Press C to calculate mapping diagnostics"
        else:
            status = (
                f"Plane mapping only | corner RMS {rms_error:.2f} mm, "
                f"max {max_error:.2f} mm"
            )
        cv2.putText(
            display, status, (15, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 255, 255), 2
        )

        for name, (px, py, box) in blocks.items():
            x, y, w, h = box
            colour = (0, 0, 255) if name == "RED" else (0, 255, 255)
            cv2.rectangle(display, (x, y), (x + w, y + h), colour, 2)
            cv2.circle(display, (px, py), 5, colour, -1)
            label = f"{name} pixel ({px},{py})"

            if H is not None:
                p = np.array([[[px, py]]], dtype=np.float32)
                mapped = cv2.perspectiveTransform(p, H)[0, 0]
                label += f" | plane ({mapped[0]:.1f}, {mapped[1]:.1f}) mm"

                outside_px = point_outside_distance_px((px, py), board_hull)
                if outside_px > 0:
                    label += f" | {outside_px:.0f}px outside board"
                else:
                    label += " | inside board area"

            cv2.putText(
                display, label, (x, max(20, y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.46, colour, 2
            )

        cv2.imshow("Table Mapping Validation - No Robot Motion", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):
            ok_now, corners_now = detect_checkerboard(gray)
            if not ok_now:
                print("Cannot calculate: checkerboard not detected in this frame.")
                continue

            H_new, rms_new, max_new = fit_mapping(corners_now)
            if H_new is None:
                print("Mapping calculation failed.")
                continue

            H = H_new
            rms_error = rms_new
            max_error = max_new
            image_xy = corners_now.reshape(-1, 2).astype(np.float32)
            board_hull = cv2.convexHull(image_xy.reshape(-1, 1, 2)).reshape(-1, 2)

            print("\n--- Mapping diagnostics ---")
            print(f"Detected inner corners: {len(image_xy)}")
            print(f"Square size assumption: {SQUARE_SIZE_MM:.1f} mm")
            print("Origin: first detected inner checkerboard corner.")
            print(f"Corner reprojection RMS: {rms_error:.3f} mm")
            print(f"Maximum corner reprojection error: {max_error:.3f} mm")
            print("Note: these are fit residuals, not an independent accuracy test.")

            for name, (px, py, _) in blocks.items():
                p = np.array([[[px, py]]], dtype=np.float32)
                mapped = cv2.perspectiveTransform(p, H)[0, 0]
                outside_px = point_outside_distance_px((px, py), board_hull)
                print(
                    f"{name}: pixel=({px}, {py}), "
                    f"board-plane=({mapped[0]:.1f}, {mapped[1]:.1f}) mm, "
                    f"distance outside checkerboard hull={outside_px:.1f} px"
                )

            print(
                "WARNING: block coordinates outside the checkerboard hull are "
                "extrapolated and may be inaccurate."
            )
            print(
                "This mapping is NOT robot-base calibration. Do not use it to "
                "command robot motion.\n"
            )

        elif key == ord("r"):
            H = None
            board_hull = None
            rms_error = None
            max_error = None
            print("Mapping reset.")

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
