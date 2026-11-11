
import pyrealsense2 as rs
import numpy as np
import cv2

pipeline = rs.pipeline()
config = rs.config()

# Request compatible colour and depth streams
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

try:
    pipeline.start(config)
    print("RealSense started. Press Q to quit.")

    align = rs.align(rs.stream.color)

    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)

        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not color_frame or not depth_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # Display depth as a visualisation; not raw distance
        depth_visual = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.03),
            cv2.COLORMAP_JET
        )

        cv2.imshow("RealSense Color", color_image)
        cv2.imshow("RealSense Depth", depth_visual)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

except Exception as exc:
    print("RealSense error:", repr(exc))

finally:
    try:
        pipeline.stop()
    except Exception:
        pass
    cv2.destroyAllWindows()
