
import pyrealsense2 as rs
import time

pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

try:
    print("Starting D415...")
    pipeline.start(config)
    print("Camera started. Reading 30 frames...")

    for i in range(30):
        frames = pipeline.wait_for_frames(timeout_ms=5000)
        color = frames.get_color_frame()
        depth = frames.get_depth_frame()

        if not color or not depth:
            print(f"Frame {i + 1}: missing stream")
            continue

        distance = depth.get_distance(320, 240)
        print(f"Frame {i + 1}: color OK, depth at center = {distance:.3f} m")

    print("Camera probe completed.")

finally:
    pipeline.stop()
    print("Camera stopped.")
