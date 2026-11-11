import pyrealsense2 as rs
import numpy as np
import cv2

print("Starting RealSense camera...", flush=True)

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

started = False

try:
    pipeline.start(config)
    started = True
    align = rs.align(rs.stream.color)

    print("Camera started. Opening live windows. Press Q to quit.", flush=True)

    while True:
        frames = pipeline.wait_for_frames()
        aligned = align.process(frames)

        color_frame = aligned.get_color_frame()
        depth_frame = aligned.get_depth_frame()

        if not color_frame or not depth_frame:
            continue

        color = np.asanyarray(color_frame.get_data())
        depth = np.asanyarray(depth_frame.get_data())

        depth_display = cv2.applyColorMap(
            cv2.convertScaleAbs(depth, alpha=0.03),
            cv2.COLORMAP_JET
        )

        cv2.imshow("RealSense - Colour", color)
        cv2.imshow("RealSense - Depth", depth_display)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except Exception as e:
    print("Camera error:", repr(e), flush=True)

finally:
    if started:
        pipeline.stop()
    cv2.destroyAllWindows()
    print("Camera stopped.", flush=True)
