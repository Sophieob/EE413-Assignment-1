import pyrealsense2 as rs
import numpy as np
import cv2

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

try:
    pipeline.start(config)

    frames = None
    for _ in range(30):
        frames = pipeline.wait_for_frames()

    color = frames.get_color_frame()
    if not color:
        raise RuntimeError("No colour frame received")

    image = np.asanyarray(color.get_data())
    cv2.rectangle(image, (410, 388), (426, 394), (0, 255, 0), 2)

    cv2.imwrite("d405_view.png", image)
    print("Saved image: d405_view.png")

finally:
    pipeline.stop()