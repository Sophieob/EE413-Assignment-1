
import sys
import numpy as np
import cv2
import pyrealsense2 as rs


def main():
    pipeline = rs.pipeline()
    config = rs.config()
    started = False

    try:
        print("Starting Intel RealSense D415...", flush=True)

        config.enable_stream(
            rs.stream.color, 640, 480, rs.format.bgr8, 30
        )
        config.enable_stream(
            rs.stream.depth, 640, 480, rs.format.z16, 30
        )

        profile = pipeline.start(config)
        started = True

        align = rs.align(rs.stream.color)
        depth_sensor = profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()

        print(f"Camera started. Depth scale: {depth_scale}", flush=True)
        print("Press Q to quit.", flush=True)

        while True:
            frames = pipeline.wait_for_frames(5000)
            aligned = align.process(frames)

            color_frame = aligned.get_color_frame()
            depth_frame = aligned.get_depth_frame()

            if not color_frame or not depth_frame:
                continue

            color = np.asanyarray(color_frame.get_data())
            raw_depth = np.asanyarray(depth_frame.get_data())
            depth_m = raw_depth.astype(np.float32) * depth_scale

            # Show only valid depth between 0.2 and 3.0 metres.
            valid = (
                np.isfinite(depth_m)
                & (depth_m >= 0.2)
                & (depth_m <= 3.0)
            )

            # Invalid pixels remain black.
            depth_display = np.zeros(raw_depth.shape, dtype=np.uint8)
            depth_display[valid] = (
                (depth_m[valid] - 0.2) / 2.8 * 255
            ).astype(np.uint8)

            depth_color = cv2.applyColorMap(
                depth_display, cv2.COLORMAP_JET
            )
            depth_color[~valid] = 0

            percentage = 100.0 * np.count_nonzero(valid) / valid.size
            cv2.putText(
                depth_color,
                f"Valid depth: {percentage:.1f}%",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

            cv2.imshow("RealSense Color", color)
            cv2.imshow("Valid Depth (0.2-3.0 m)", depth_color)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break

    except Exception as exc:
        print(f"\nRealSense error: {exc}", file=sys.stderr, flush=True)
        return 1

    finally:
        if started:
            try:
                pipeline.stop()
                print("Camera stopped.", flush=True)
            except Exception as exc:
                print(f"Camera shutdown warning: {exc}", flush=True)

        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    sys.exit(main())
