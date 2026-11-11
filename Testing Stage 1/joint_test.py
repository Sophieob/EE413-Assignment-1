import math
from rtde_control import RTDEControlInterface
from rtde_receive import RTDEReceiveInterface

from local_config import ROBOT_IP

SPEED = 0.05
ACCELERATION = 0.05
DELTA = math.radians(2.0)

rtde_r = None
rtde_c = None

try:
    rtde_r = RTDEReceiveInterface(ROBOT_IP)
    current_q = rtde_r.getActualQ()

    # Add 2 degrees to every joint
    target_q = [q + DELTA for q in current_q]

    joint_names = [
        "Base", "Shoulder", "Elbow",
        "Wrist 1", "Wrist 2", "Wrist 3"
    ]

    print("\nCurrent and proposed joint angles:")
    for name, current, target in zip(
        joint_names, current_q, target_q
    ):
        print(
            f"{name}: {math.degrees(current):.2f}°"
            f" -> {math.degrees(target):.2f}°"
        )

    print("\nAll six joints will change by +2 degrees.")
    confirm = input("Type MOVE to execute: ")

    if confirm == "MOVE":
        rtde_c = RTDEControlInterface(ROBOT_IP)
        result = rtde_c.moveJ(
            target_q, SPEED, ACCELERATION
        )
        print("moveJ result:", result)
    else:
        print("Cancelled. No motion command sent.")

finally:
    if rtde_c is not None:
        rtde_c.stopScript()
        rtde_c.disconnect()

    if rtde_r is not None:
        rtde_r.disconnect()

    print("RTDE connections closed.")
