# nuitka-project: --onefile
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml
# nuitka-project: --windows-icon-from-ico=icon.ico
# nuitka-project: --onefile-windows-splash-screen-image={MAIN_DIRECTORY}/splash.png
# nuitka-project: --file-version=1.0
# nuitka-project: --company-name=KabanTechnologies
# nuitka-project: --product-name=TGNote
# nuitka-project: --disable-console
#
# Поддерживает splash. Без него - юзай --mingw64
# nuitka-project: --msvc=latest

import os
import random
import tempfile
import threading
import time
import tkinter as tk

import pystray
from dotenv import dotenv_values
from interception import auto_capture_devices, press
from PIL import Image
from pyautogui import ImageNotFoundException, locate, screenshot
from pyrogram import Client
from pytimedinput import timedKey
from requests import get
from pynput import keyboard

auto_capture_devices(keyboard=True, mouse=True)

tray_icon = Image.open("icon.ico")
config = dotenv_values(".env")
message_txt = "Прок прок прок!!!"
message_voice_list = [
    "/s Кабан, вставай, <[300]> пора хрюкать",
    "/s Истекаю кровью как свинья на бойне",
    "/s Пора, <[500]> брат",
    "/s Застелил кровать, <[500]> пора убивать",
    "/s Н+оу каб+анас, <[500]> си, <[500]> сеньёре",
]



#   Функции основной программы.


def wait_and_accept_several_buttons():
    buttons = ["button1.png", "button2.png", "button3.png"]
    while 1:
        temp_scr = screenshot()
        for button in buttons:
            try:
                locate(button, temp_scr, confidence=0.8)
                if button == "button1.png":
                    press("f12")
                    print("Proc found!")
                    print("Alice is enabled: ", enable_alice)
                    return
                elif button == "button2.png":
                    press("f12")
                    print("Accept button found. Confirmed.")
                elif button == "button3.png":
                    print("Proc found!")
                    print("Alice is enabled: ", enable_alice)
                    return
            except (ImageNotFoundException, OSError):
                pass
        print("Waitin for proc...")
        print("Alice is enabled: ", enable_alice)
        time.sleep(5)


def send_txt_msg():
    """Оповещает в ТГ чат ботом."""
    url = (
        f"https://api.telegram.org/bot{config['TOKEN']}"
        f"/sendMessage?chat_id={config['CHAT_ID_BOT']}&text={message_txt}"
    )
    get(url)


def mainfunc():
    wait_and_accept_several_buttons()
    send_txt_msg()
    exit_flag.set()


#   Функции трея.


def on_click_alice(icon, item):
    global enable_alice
    enable_alice = not item.checked


def on_click_exit(icon, item):
    icon.stop()
    exit_flag.set()


def trayfunc():
    global enable_alice
    tray = pystray.Icon(
        "TGNote",
        tray_icon,
        menu=pystray.Menu(
            pystray.MenuItem(
                "Отправлять уведомления Алисе",
                on_click_alice,
                checked=lambda item: enable_alice,
            ),
            pystray.MenuItem("Выход", on_click_exit),
        ),
    )
    tray.run()


# Функция оповещения Алисы.


def send_voice_msg():
    """Звуковое оповещение на колонку Алиса."""
    app = Client(config["CLIENT_NAME"], config["ACC_ID"], config["ACC_HASH"])
    app.start()
    app.send_message(
        "@alice_speaker_bot",
        message_voice_list[random.randint(0, len(message_voice_list) - 1)],
    )
    app.stop()
    print("sound sent")


#   Функции инициализации.


# ===================================================================================================================================
def leave_splash(root):
    choice_was_made_flag.set()
    root.destroy()

def splash():
    # create the main window
    root = tk.Tk()

    # disable the window bar
    root.overrideredirect(1)

    # set trasparency and make the window stay on top
    root.attributes('-transparentcolor', 'gray8', '-topmost', True)

    # set the background image
    psg = tk.PhotoImage(file='splash.png')
    tk.Label(root, bg='gray8', image=psg).pack()

    # move the window to center
    root.eval('tk::PlaceWindow . Center')

    # schedule the window to close after 4 seconds
    root.after(10000, leave_splash, root)

    # run the main loop
    root.mainloop()

def on_press(key):
    global enable_alice
    try:
        key_pressed = key.char
        if key_pressed == '1':
            enable_alice = False
            choice_was_made_flag.set()
        elif key_pressed == "2":
            print('aqweqwe')
            enable_alice = True
            choice_was_made_flag.set()
    except:
        pass

def key_checker():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    choice_was_made_flag.wait()
    listener.stop()


# ===================================================================================================================================


# Основная программа.


if __name__ == "__main__":
    choice_was_made_flag = threading.Event()
    enable_alice = False
    thread_splash = threading.Thread(target=splash, daemon=True)
    thread_splash.start()

    key_listener_thread = threading.Thread(target=key_checker, daemon=True)
    key_listener_thread.start()

    choice_was_made_flag.wait()

    exit_flag = threading.Event()

    daemon_thread_main = threading.Thread(target=mainfunc, daemon=True)
    daemon_thread_main.start()

    daemon_thread_tray = threading.Thread(target=trayfunc, daemon=True)
    daemon_thread_tray.start()

    exit_flag.wait()

    if enable_alice and not daemon_thread_main.is_alive():
        send_voice_msg()  # аккуратно со спамом, больше 10 в час не советуют (клиент апи тг)
        # pyrogram.Client должен быть в main thread'е, async и многопоточность
