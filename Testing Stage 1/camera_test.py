
import cv2

# Try the default camera first
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera 0 unavailable. Trying camera 1...")
    camera.release()
    camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("ERROR: Could not open a webcam.")
    print("Check the camera connection and macOS camera permissions.")
    raise SystemExit(1)

print("Camera connected!")
print("Press Q to quit.")

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read a camera frame.")
        break

    cv2.imshow("UR5e Project - Camera Test", frame)

    # Quit when Q is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
