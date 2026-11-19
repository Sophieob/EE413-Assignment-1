
"""
Collect matching camera-frame and robot-base-frame points.
SAFETY: This script reads robot state only. It never commands movement.
"""

import csv
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs
import rtde_receive

from local_config import ROBOT_IP


OUTPUT = Path(
    f"camera_robot_points_{datetime.now():%Y%m%d_%H%M%S}.csv"
)

selected_pixel = None


def mouse_callback(event, x, y, flags, param):
    global selected_pixel

    if event == cv2.EVENT_LBUTTONDOWN:
        selected_pixel = (x, y)
        print(f"Selected image pixel: ({x}, {y})")


def main():
    pipeline = rs.pipeline()
    config = rs.config()

    config.enable_stream(
        rs.stream.color, 640, 480, rs.format.bgr8, 30
    )
    config.enable_stream(
        rs.stream.depth, 640, 480, rs.format.z16, 30
    )

    align = rs.align(rs.stream.color)
    robot = None

    try:
        print(f"Connecting to UR5e at {ROBOT_IP}...")
        robot = rtde_receive.RTDEReceiveInterface(ROBOT_IP)

        pipeline.start(config)
        print("D405 started.")
        print(f"Output CSV: {OUTPUT.resolve()}")

        cv2.namedWindow("Calibration capture")
        cv2.setMouseCallback(
            "Calibration capture", mouse_callback
        )

        with OUTPUT.open("w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "point_id",
                "pixel_x", "pixel_y", "depth_m",
                "cam_x_m", "cam_y_m", "cam_z_m",
                "base_x_m", "base_y_m", "base_z_m",
                "tcp_rx", "tcp_ry", "tcp_rz"
            ])

            point_id = 0

            while True:
                frames = pipeline.wait_for_frames()
                aligned = align.process(frames)

                color = aligned.get_color_frame()
                depth = aligned.get_depth_frame()

                if not color or not depth:
                    continue

                image = np.asanyarray(color.get_data())
                depth_intrinsics = (
                    depth.profile
                    .as_video_stream_profile()
                    .intrinsics
                )

                if selected_pixel is not None:
                    x, y = selected_pixel
                    cv2.circle(image, (x, y), 6, (0, 255, 0), 2)

                cv2.putText(
                    image,
                    "Click point; position TCP there; press S to save",
                    (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48, (255, 255, 255), 1
                )
                cv2.imshow("Calibration capture", image)

                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break

                if key != ord("s"):
                    continue

                if selected_pixel is None:
                    print("Click a calibration point first.")
                    continue

                x, y = selected_pixel
                depth_m = depth.get_distance(x, y)

                if depth_m <= 0:
                    print("Invalid depth. Click a visible point again.")
                    continue

                # 3D point in the D405 camera coordinate frame.
                cam_xyz = rs.rs2_deproject_pixel_to_point(
                    depth_intrinsics, [x, y], depth_m
                )

                # Read-only: actual TCP pose in robot base coordinates.
                tcp_pose = robot.getActualTCPPose()
                base_xyz = tcp_pose[:3]
                tcp_rot = tcp_pose[3:]

                print("\nCheck correspondence before saving:")
                print(f"Camera XYZ (m): {cam_xyz}")
                print(f"Robot TCP XYZ (m): {base_xyz}")
                print("Press S only if the TCP is at the selected point.")

                writer.writerow([
                    point_id, x, y, depth_m,
                    *cam_xyz, *base_xyz, *tcp_rot
                ])
                file.flush()

                point_id += 1
                print(f"Saved calibration pair {point_id}.")

    finally:
        pipeline.stop()
        if robot is not None:
            robot.disconnect()
        cv2.destroyAllWindows()
        print("Capture stopped. No movement commands were sent.")


if __name__ == "__main__":
    main()
