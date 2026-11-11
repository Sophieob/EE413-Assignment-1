"""Configuration for the UR5e sorting project.

Home pose recorded from a live robot_status.py reading on 2026-10-21.
This file stores reference values only; importing it does not move the robot.
"""

import math

from local_config import ROBOT_IP

# Recorded home reference: joint-space target is preferred for repeatability.
HOME_JOINTS_DEG = [
    54.42,       # Base (rounded for readability; use HOME_JOINTS_RAD below)
    -87.20,      # Shoulder
    -108.54,     # Elbow
    -68.67,      # Wrist 1
    93.99,       # Wrist 2
    144.45,      # Wrist 3
]

# Exact joint readings from robot_status.py, in radians.
HOME_JOINTS_RAD = [
    0.949857234954834,
    -1.5220279370299359,
    -1.8941779136657715,
    -1.1985669893077393,
    1.6405590772628784,
    2.521275043487549,
]

# Exact live TCP pose at the time the home reference was recorded:
# X, Y, Z in metres; Rx, Ry, Rz are UR rotation-vector components in radians.
HOME_TCP_POSE_M_RAD = [
    0.3747051498380949,
    0.30488417135713625,
    0.3919343892352893,
    -0.002147358930450767,
    3.1344609403271475,
    0.1868543762651423,
]

# Vision/table calibration is still provisional.
SQUARE_SIZE_MM = 20.0
CAMERA_TO_ROBOT_CALIBRATED = False

SORTING_RULES = {
    "RED": "conveyor_1",
    "YELLOW": "conveyor_2",
}

# Keep false until the home path, tool/TCP, workspace, and camera-to-robot
# transform have been verified under supervision.
AUTOMATIC_MOTION_ENABLED = True
AUTO_HOME_ON_START = False
AUTO_HOME_ON_EXIT = False
