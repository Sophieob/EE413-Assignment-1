
import pyrealsense2 as rs
import numpy as np

pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

try:
    profile = pipeline.start(config)
    sensor = profile.get_device().first_depth_sensor()
    scale = sensor.get_depth_scale()

    print(f"Depth scale: {scale} metres per unit")
    print("Collecting depth frames...")

    for _ in range(30):
        frames = pipeline.wait_for_frames(timeout_ms=5000)
        depth_frame = frames.get_depth_frame()

    depth_raw = np.asanyarray(depth_frame.get_data())
    depth_m = depth_raw.astype(np.float32) * scale

    valid = depth_m > 0
    valid_distances = depth_m[valid]

    print(f"Image size: {depth_m.shape}")
    print(f"Valid pixels: {valid.sum()} / {depth_m.size}")
    print(f"Valid percentage: {100 * valid.mean():.2f}%")

    # Report plausible tabletop-range measurements separately.
    tabletop = valid_distances[
        (valid_distances >= 0.2) & (valid_distances <= 3.0)
    ]
    print(f"Pixels between 0.2 and 3.0 m: {len(tabletop)}")

    if len(valid_distances):
        print("All nonzero depth readings (metres):")
        print("  5th percentile:", np.percentile(valid_distances, 5))
        print("  Median:", np.median(valid_distances))
        print("  95th percentile:", np.percentile(valid_distances, 95))

    if len(tabletop):
        print("Tabletop-range median (metres):", np.median(tabletop))
    else:
        print("No readings in the selected tabletop range.")

finally:
    pipeline.stop()
    print("Camera stopped.")
