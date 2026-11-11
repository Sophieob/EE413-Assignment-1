
# ============================================================
# UR5e CAMERA-TO-ROBOT CALIBRATION CONFIGURATION
# Project: Red and Yellow Block Sorting
# Robot: UR5e
# ============================================================

import math

# ------------------------------------------------------------
# Robot connection
# ------------------------------------------------------------

ROBOT_IP = "actual_robot_ip"

# ------------------------------------------------------------
# Calibration reference TCP pose
# Recorded from the UR5e teach pendant.
#
# Position: metres
# Orientation: rotation vector in radians
# ------------------------------------------------------------

CALIBRATION_START = {
    "position_m": (
        0.36779,
        0.34213,
        -0.01922,
    ),

    "rotation_vector_rad": (
        2.104,
        -2.383,
        -0.072,
    ),
}

# ------------------------------------------------------------
# Calibration reference joint configuration
# Recorded from the UR5e teach pendant.
#
# Joint order:
# Base, Shoulder, Elbow, Wrist 1, Wrist 2, Wrist 3
# ------------------------------------------------------------

CALIBRATION_START_JOINTS_DEG = [
    58.04,
    -90.61,
    -106.08,
    -70.48,
    91.97,
    65.13,
]

# Convert degrees to radians for RTDE motion APIs.
CALIBRATION_START_JOINTS_RAD = [
    math.radians(angle)
    for angle in CALIBRATION_START_JOINTS_DEG
]

# ------------------------------------------------------------
# Checkerboard configuration
# Each square is 20 mm per side, as reported.
# ------------------------------------------------------------

SQUARE_SIZE_MM = 20.0

# ------------------------------------------------------------
# Camera calibration status
# False until the camera-to-robot transformation has
# been measured and validated.
# ------------------------------------------------------------

CAMERA_TO_ROBOT_CALIBRATED = False

# ------------------------------------------------------------
# Sorting configuration
# Red blocks   -> Conveyor 1
# Yellow blocks -> Conveyor 2
# ------------------------------------------------------------

SORTING_RULES = {
    "red": "conveyor_1",
    "yellow": "conveyor_2",
}

# ------------------------------------------------------------
# Safety: configuration only.
# This file does not connect to or move the robot.
# ------------------------------------------------------------

AUTOMATIC_MOTION_ENABLED = False
