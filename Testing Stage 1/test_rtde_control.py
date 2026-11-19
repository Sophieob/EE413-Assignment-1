
import rtde_control
import rtde_receive

ROBOT_IP = "192.168.77.2"

rtde_r = None
rtde_c = None

try:
    print("Connecting to UR5e at", ROBOT_IP)

    rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
    print("RTDE Receive connection: OK")

    rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
    print("RTDE Control connection: OK")

    joints = rtde_r.getActualQ()
    print("Current joint positions (radians):", joints)

    tcp_pose = rtde_r.getActualTCPPose()
    print("Current TCP pose (metres/radians):", tcp_pose)

finally:
    if rtde_c is not None:
        rtde_c.disconnect()
        print("RTDE Control disconnected.")

    if rtde_r is not None:
        rtde_r.disconnect()
        print("RTDE Receive disconnected.")
