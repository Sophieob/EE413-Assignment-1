import pyrealsense2 as rs
import numpy as np
import time

pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(
    rs.stream.depth, 640, 480, rs.format.z16, 30
)
config.enable_stream(
    rs.stream.color, 640, 480, rs.format.bgr8, 30
)

try:
    profile = pipeline.start(config)

    align = rs.align(rs.stream.color)
    depth_scale = (
        profile.get_device()
        .first_depth_sensor()
        .get_depth_scale()
    )

    print("D405 started; depth aligned to colour.")
    print("Keep the camera stationary.")

    for _ in range(30):
        frames = pipeline.wait_for_frames()
        aligned = align.process(frames)

    for i in range(5):
        frames = pipeline.wait_for_frames()
        aligned = align.process(frames)

        depth_frame = aligned.get_depth_frame()
        if not depth_frame:
            print("No aligned depth frame.")
            continue

        depth_image = np.asanyarray(depth_frame.get_data())

        # Same region as the green rectangle in the colour image
        roi = depth_image[388:394, 410:426]

        metres = roi[roi > 0] * depth_scale

        if metres.size:
            print(
                f"Reading {i+1}: "
                f"median depth = {np.median(metres):.3f} m "
                f"({metres.size} valid pixels)"
            )
        else:
            print(f"Reading {i+1}: No valid depth pixels.")

        time.sleep(0.5)

finally:
    pipeline.stop()
    print("Depth test finished.")