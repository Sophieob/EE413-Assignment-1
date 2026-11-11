
import pyrealsense2 as rs
import sys

pipeline = rs.pipeline()
started = False

try:
    print("Creating configuration...", flush=True)

    config = rs.config()
    config.enable_stream(
        rs.stream.color, 640, 480, rs.format.bgr8, 30
    )
    config.enable_stream(
        rs.stream.depth, 640, 480, rs.format.z16, 30
    )

    print("Starting camera...", flush=True)
    profile = pipeline.start(config)
    started = True

    print("Camera started successfully.", flush=True)

    for i in range(10):
        frames = pipeline.wait_for_frames(5000)
        color = frames.get_color_frame()
        depth = frames.get_depth_frame()

        print(
            f"Frame {i + 1}: "
            f"color={bool(color)}, depth={bool(depth)}",
            flush=True
        )

finally:
    if started:
        pipeline.stop()
        print("Camera stopped.", flush=True)

