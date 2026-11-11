import rtde.rtde as rtde
import rtde.rtde_config as rtde_config

robot = rtde.RTDE("actual_robot_ip", 30004)
config = rtde_config.ConfigFile("robot_status.xml")

try:
    robot.connect()
    print("Controller version:", robot.get_controller_version())

    names, types = config.get_recipe("state")
    if not robot.send_output_setup(names, types):
        raise RuntimeError("RTDE output setup failed")

    if not robot.send_start():
        raise RuntimeError("RTDE data exchange failed to start")

    state = robot.receive()
    if state is None:
        raise RuntimeError("No state data received")

    print("Robot mode:", state.robot_mode,
          "(7 = Running)")
    print("Safety status:", state.safety_status,
          "(1 = Normal)")
    print("Program state:", state.runtime_state,
          "(2 = Running, 1 = Stopped)")
    print("Joint positions (rad):", state.actual_q)
    print("TCP pose (m, rotation vector):", state.actual_TCP_pose)

finally:
    robot.disconnect()
    print("Disconnected; no motion commands sent.")
