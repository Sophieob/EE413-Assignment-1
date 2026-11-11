
import pyrealsense2 as rs
import numpy as np
import cv2

WINDOW = "RealSense - Hover over a block"
mouse_x, mouse_y = -1, -1


def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y

    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x, mouse_y = x, y


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
    print("Starting RealSense D415...", flush=True)
    pipeline.start(config)
    started = True

    align = rs.align(rs.stream.color)

    cv2.namedWindow(WINDOW)
    cv2.setMouseCallback(WINDOW, mouse_callback)

    print("Move your mouse over a block to measure depth.")
    print("Press Q in the camera window to quit.", flush=True)

    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)

        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not color_frame or not depth_frame:
            continue

        image = np.asanyarray(color_frame.get_data())

        x, y = mouse_x, mouse_y
        depth_text = "Move mouse over a block"

        if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
            # Use a small neighbourhood to reduce noisy readings.
            distances = []

            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    px, py = x + dx, y + dy

                    if 0 <= px < 640 and 0 <= py < 480:
                        distance = depth_frame.get_distance(px, py)

                        if 0.10 < distance < 3.0:
                            distances.append(distance)

            if distances:
                depth_m = float(np.median(distances))
                depth_text = f"Depth: {depth_m:.3f} m ({depth_m * 100:.1f} cm)"
            else:
                depth_text = "No valid depth at this point"

            cv2.drawMarker(
                image, (x, y), (0, 255, 0),
                cv2.MARKER_CROSS, 18, 2
            )

        cv2.rectangle(image, (5, 5), (470, 45), (0, 0, 0), -1)
        cv2.putText(
            image, depth_text, (15, 32),
            cv2.FONT_HERSHEY_SIMPLEX, 0.65,
            (0, 255, 0), 2
        )

        cv2.imshow(WINDOW, image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except Exception as e:
    print("RealSense error:", repr(e), flush=True)

finally:
    if started:
        pipeline.stop()

    cv2.destroyAllWindows()
    print("Camera stopped.", flush=True)
