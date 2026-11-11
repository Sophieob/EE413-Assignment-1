import rtde_control

ROBOT_IP = "actual_robot_ip"

rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)

print("RTDE Control connection: OK")

rtde_c.disconnect()
print("Disconnected safely.")
