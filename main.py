from services.qr_generator import generate_qr
import utils.camera
import threading
import time

name = input("Podaj swoje imie: ")

qr_text = f"{name}"
generate_qr(qr_text, f"{name}_qr.png")

print("this is main")
t = threading.Thread(target=utils.camera.camera)
t.start()


print("Main Thread is running")
time.sleep(5)
print("Stopping Camera")
utils.camera.z = False



