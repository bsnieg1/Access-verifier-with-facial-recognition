from services.qr_generator import generate_qr
from services.user_service import add_user, get_user
import utils.camera
import threading
import time

while True:
    print("this is main")

    print("1 - Dodaj użytkownika")
    print("2 - Skanuj QR")
    print("3 - Wyjście")
    choice = input("Wybierz opcję: ")

    if choice == "1":
        name = input("Podaj imię: ")
        user_id = add_user(name)

        generate_qr(user_id, f"user_{user_id}.png")
        print(f"Użytkownik {name} dodany z ID {user_id}")

    elif choice == "2":

        t = threading.Thread(target=utils.camera.camera)
        t.start()
        print("Main Thread is running")

    elif choice == "3":
        break




