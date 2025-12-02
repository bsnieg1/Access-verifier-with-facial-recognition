import utils.camera
import threading
import time

print("this is main")
t = threading.Thread(target=utils.camera.camera)
t.start()


print("Main Thread is running")
time.sleep(15)
print("Stopping Camera")
utils.camera.z = False

