
import math
import sys

import rtde_control
import rtde_receive
import calibration_config as config

SPEED = 0.45       # rad/s
ACCELERATION = 0.30  # rad/s^2
TOLERANCE_DEG = 2.0


def main():
    if not config.AUTOMATIC_MOTION_ENABLED:
        print("Automatic motion is disabled in calibration_config.py.")
        print("This script will not move the robot.")
        print("After validating the trajectory, enable motion explicitly.")
        return

    receiver = None
    controller = None

    try:
        receiver = rtde_receive.RTDEReceiveInterface(config.ROBOT_IP)

        current_q = receiver.getActualQ()
        target_q = config.HOME_JOINTS_RAD

        print("\nCURRENT POSITION -> SAVED HOME")
        for i, (current, target) in enumerate(
            zip(current_q, target_q), start=1
        ):
            print(
                f"J{i}: {math.degrees(current):.2f}°"
                f" -> {math.degrees(target):.2f}°"
            )

        print("\nCheck the complete swept path for collisions.")
        print("Keep the robot supervised with the pendant accessible.")
        confirmation = input(
            "Type RETURN_HOME to request the move, or anything else to cancel: "
        )

        if confirmation != "RETURN_HOME":
            print("Cancelled. No motion command sent.")
            return

        # Re-read immediately before the motion request.
        current_q = receiver.getActualQ()

        print("\nMotion request enabled by configuration and confirmation.")
        controller = rtde_control.RTDEControlInterface(config.ROBOT_IP)

        result = controller.moveJ(
            target_q,
            SPEED,
            ACCELERATION,
        )

        print("moveJ result:", result)

        # Verify actual joints after the movement request.
        final_q = receiver.getActualQ()
        errors_deg = [
            abs(math.degrees(actual - target))
            for actual, target in zip(final_q, target_q)
        ]

        print("\nFINAL HOME CHECK")
        for i, error in enumerate(errors_deg, start=1):
            print(f"J{i}: error = {error:.2f}°")

        if all(error <= TOLERANCE_DEG for error in errors_deg):
            print("Result: AT HOME within tolerance.")
        else:
            print("Result: HOME NOT CONFIRMED.")

    except Exception as exc:
        print(f"Robot operation failed: {exc}")
        sys.exit_code = 1

    finally:
        if controller is not None:
            try:
                controller.stopScript()
            except Exception:
                pass
            try:
                controller.disconnect()
            except Exception:
                pass

        if receiver is not None:
            try:
                receiver.disconnect()
            except Exception:
                pass

        print("RTDE connections closed.")


if __name__ == "__main__":
    main()
