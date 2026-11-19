import time
import cv2
import numpy as np
import pyrealsense2 as rs
from collections import deque

pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(
    rs.stream.color, 640, 480, rs.format.bgr8, 30
)
config.enable_stream(
    rs.stream.depth, 640, 480, rs.format.z16, 30
)

started = False

try:
    profile = pipeline.start(config)
    started = True

    align = rs.align(rs.stream.color)
    device = profile.get_device()
    depth_scale = (
        device.first_depth_sensor().get_depth_scale()
    )

    print("Connected camera:", device.get_info(rs.camera_info.name))
    print("Detecting red and yellow blocks with depth.")
    print("Press Q to quit.")

    # Intrinsics of the colour image, used for 3D projection
    color_profile = profile.get_stream(
        rs.stream.color
    ).as_video_stream_profile()
    intrinsics = color_profile.get_intrinsics()

    kernel = np.ones((5, 5), np.uint8)
    last_print = 0

    # Store the latest 9 XYZ measurements for each block.
    xyz_history = {
        "RED": deque(maxlen=9),
        "YELLOW": deque(maxlen=9),
    }

    while True:
        frames = pipeline.wait_for_frames(5000)
        aligned = align.process(frames)

        color_frame = aligned.get_color_frame()
        depth_frame = aligned.get_depth_frame()

        if not color_frame or not depth_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())
        raw_depth = np.asanyarray(depth_frame.get_data())
        depth_m = raw_depth.astype(np.float32) * depth_scale

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Restrict detection to the visible tabletop.
        table_mask = np.zeros(frame.shape[:2], dtype=np.uint8)

        table_polygon = np.array([
            [0, 260],
            [320, 280],
            [639, 340],
            [639, 479],
            [0, 479]
        ], dtype=np.int32)

        cv2.fillPoly(table_mask, [table_polygon], 255)

        # Red: hue wraps around the HSV scale
        red_mask = (
            cv2.inRange(
                hsv, np.array([0, 100, 70]),
                np.array([10, 255, 255])
            )
            | cv2.inRange(
                hsv, np.array([170, 100, 70]),
                np.array([179, 255, 255])
            )
        )

        # Yellow
        yellow_mask = cv2.inRange(
            hsv, np.array([15, 70, 70]),
            np.array([40, 255, 255])
        )

        detections = [
            (red_mask, "RED", (0, 0, 255)),
            (yellow_mask, "YELLOW", (0, 255, 255)),
        ]

        found = []

        for mask, label, box_colour in detections:
            mask = cv2.bitwise_and(mask, table_mask)
            mask = cv2.morphologyEx(
                mask, cv2.MORPH_OPEN, kernel
            )

           # Find the contours in the colour mask.
            contours, _ = cv2.findContours(
                mask,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            # Keep only the largest detected region of this colour.
            contours = sorted(
                contours,
                key=cv2.contourArea,
                reverse=True
            )[:1]

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 500:
                    continue

                x, y, w, h = cv2.boundingRect(contour)

                # Reject very thin regions; this is a basic filter,
                # not a guarantee that the object is a block.
                if min(w, h) == 0 or max(w, h) / min(w, h) > 2.5:
                    continue

                moments = cv2.moments(contour)
                if moments["m00"] == 0:
                    continue

                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])

                # Median of valid depth values in a small centre patch

                # Estimate depth using the interior of the detected block
                object_mask = np.zeros(mask.shape, dtype=np.uint8)
                cv2.drawContours(
                    object_mask, [contour], -1, 255, thickness=-1
                )

                # Remove boundary pixels to reduce background contamination
                object_mask = cv2.erode(
                    object_mask,
                    np.ones((5, 5), np.uint8),
                    iterations=1,
                )

                # Select only valid depth pixels inside this contour
                valid_region = (
                    (object_mask > 0)
                    & np.isfinite(depth_m)
                    & (depth_m > 0)
                    & (depth_m >= 0.40)
                    & (depth_m <= 0.85)
                )

                valid_depths = depth_m[valid_region]

                if valid_depths.size < 20:
                    depth_text = "Z unavailable"
                    xyz_text = None
                else:
                    z = float(np.median(valid_depths))

                    # Project the detected centre into camera-frame XYZ
                    z = float(np.median(valid_depths))

                    # Project the detected centre into camera-frame XYZ.
                    point = rs.rs2_deproject_pixel_to_point(
                        intrinsics, [float(cx), float(cy)], z
                    )
                    X, Y, Z = point

                    # Keep recent measurements for this block.
                    xyz_history[label].append((X, Y, Z))

                    # Use the median across recent frames to reduce jumps.
                    smoothed_xyz = np.median(
                        np.array(xyz_history[label]), axis=0
                    )
                    X, Y, Z = map(float, smoothed_xyz)

                    depth_text = f"Z={Z:.3f} m"
                    xyz_text = (X, Y, Z)
                    found.append((label, X, Y, Z))

                cv2.putText(
                    frame,
                    f"Depth pixels: {valid_depths.size}",
                    (x, min(y + h + 20, 465)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    box_colour,
                    1,
                )
                cv2.rectangle(
                    frame, (x, y), (x + w, y + h),
                    box_colour, 2
                )
                cv2.circle(
                    frame, (cx, cy), 4, box_colour, -1
                )
                cv2.putText(
                    frame, f"{label} BLOCK {depth_text}",
                    (x, max(y - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    box_colour, 2
                )

        # Print coordinates at most once per second
        now = time.time()
        if found and now - last_print >= 1.0:
            for label, X, Y, Z in found:
                print(
                    f"{label}: camera XYZ = "
                    f"({X:.3f}, {Y:.3f}, {Z:.3f}) m"
                )
            last_print = now

        cv2.imshow("D405 Red/Yellow Detection + Depth", frame)

        if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
            break

except Exception as exc:
    print("Error:", exc)

finally:
    if started:
        pipeline.stop()
    cv2.destroyAllWindows()
    print("Camera stopped.")
