
import math

import rtde_receive
import calibration_config as config

TOLERANCE_DEG = 2.0


def main():
    receiver = None

    try:
        receiver = rtde_receive.RTDEReceiveInterface(config.ROBOT_IP)

        current = receiver.getActualQ()
        target = config.HOME_JOINTS_RAD

        print("Home position check — READ ONLY")
        print("-" * 50)

        all_close = True

        for index, (actual, home) in enumerate(zip(current, target), start=1):
            difference_deg = math.degrees(actual - home)
            actual_deg = math.degrees(actual)
            home_deg = math.degrees(home)
            is_close = abs(difference_deg) <= TOLERANCE_DEG
            all_close = all_close and is_close

            print(
                f"J{index}: current={actual_deg:8.2f}°, "
                f"home={home_deg:8.2f}°, "
                f"difference={difference_deg:+7.2f}° "
                f"{'OK' if is_close else 'OUTSIDE TOLERANCE'}"
            )

        print("-" * 50)
        print("Result:", "AT HOME" if all_close else "NOT AT HOME")
        print(f"Per-joint tolerance: ±{TOLERANCE_DEG:.1f}°")
        print("No robot movement commands were sent.")

    finally:
        if receiver is not None:
            receiver.disconnect()


if __name__ == "__main__":
    main()
