
import pyrealsense2 as rs
import numpy as np

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

try:
    profile = pipeline.start(config)
    scale = profile.get_device().first_depth_sensor().get_depth_scale()

    print("Keep the camera still and aim at the tabletop or block.")

    samples = []

    for _ in range(30):
        frames = pipeline.wait_for_frames()
        frame = frames.get_depth_frame()
        if not frame:
            continue

        depth = np.asanyarray(frame.get_data()).astype(np.float32) * scale

        # Larger region around the image centre
        region = depth[180:300, 240:400]
        valid = region[(region >= 0.2) & (region <= 3.0)]

        if len(valid):
            samples.append(np.median(valid))

    if samples:
        print(f"Valid frames: {len(samples)} / 30")
        print(f"Median region depth: {np.median(samples):.3f} m")
        print(f"Minimum frame median: {np.min(samples):.3f} m")
        print(f"Maximum frame median: {np.max(samples):.3f} m")
    else:
        print("No valid depth readings. Try a textured, non-reflective surface.")

finally:
    pipeline.stop()
    print("Camera stopped.")
