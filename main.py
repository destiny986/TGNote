# nuitka-project: --mingw64
# nuitka-project: --onefile
# nuitka-project: --windows-console-mode=disable
#
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-qt-plugins=qml
#
# nuitka-project: --windows-icon-from-ico=data/icon.ico
# nuitka-project: --file-version=1.0
# nuitka-project: --company-name=KabanTechnologies
# nuitka-project: --product-name=TGNote
# nuitka-project: --output-filename=TGNote
#
# nuitka-project: --enable-plugin=tk-inter
# nuitka-project: --include-data-dir=data/={MAIN_DIRECTORY}/data


import os
import random
import threading
import time
import tkinter as tk

from dotenv import dotenv_values
from interception import auto_capture_devices, key_down, key_up
from PIL import Image
from pyautogui import ImageNotFoundException, locate, screenshot
from pynput import keyboard
from pyrogram import Client
from pystray import Icon, Menu, MenuItem
from requests import get

auto_capture_devices(keyboard=True, mouse=True)

tray_icon = Image.open(os.path.join(os.path.dirname(__file__), "data/icon.ico"))
config = dotenv_values(".env")
message_txt = "Прок прок прок!!!"
message_voice_list = [
    "/s Кабан, вставай, <[300]> пора хрюкать",
    "/s Истекаю кровью как свинья на бойне",
    "/s Пора, <[500]> брат",
    "/s Застелил кровать, <[500]> пора убивать",
    "/s Н+оу каб+анас, <[500]> си, <[500]> сеньёре",
]
timeout_splash = 10
timeout_search = 5


def random_click(key):
    key_down(key)
    time.sleep(random.uniform(0.2, 0.8))
    key_up(key)
    return


def wait_and_accept_several_buttons():
    """Поиск кнопок и подтверждение нажатия."""
    buttons = [
        os.path.join(os.path.dirname(__file__), "data/button1.png"),
        os.path.join(os.path.dirname(__file__), "data/button2.png"),
        os.path.join(os.path.dirname(__file__), "data/button3.png"),
    ]
    while 1:
        temp_scr = screenshot()
        for button in buttons:
            try:
                locate(button, temp_scr, confidence=0.8)
                if button == buttons[0]:
                    random_click("f12")
                    print("Proc found!")
                    print("Alice is enabled: ", enable_alice)
                    return
                elif button == buttons[1]:
                    random_click("f12")
                    print("Accept button found. Confirmed.")
                elif button == buttons[2]:
                    print("Proc found!")
                    print("Alice is enabled: ", enable_alice)
                    return
            except (ImageNotFoundException, OSError):
                pass
        print("Waitin for proc...")
        print("Alice is enabled: ", enable_alice)
        time.sleep(timeout_search)


def send_txt_msg():
    """Оповещает в ТГ чат ботом."""
    url = (
        f"https://api.telegram.org/bot{config['TOKEN']}"
        f"/sendMessage?chat_id={config['CHAT_ID_BOT']}&text={message_txt}"
    )
    get(url)


def mainfunc():
    """Функция для отдельного от трея потока."""
    wait_and_accept_several_buttons()
    send_txt_msg()
    exit_flag.set()


def on_click_alice(icon, item):
    """Переключатель Алисы в трее."""
    global enable_alice
    enable_alice = not item.checked


def on_click_exit(icon, item):
    """Трей клик - Выход."""
    icon.stop()
    exit_flag.set()


def trayfunc():
    """Функции трея."""
    global enable_alice
    tray = Icon(
        "TGNote",
        tray_icon,
        menu=Menu(
            MenuItem(
                "Отправлять уведомления Алисе",
                on_click_alice,
                checked=lambda item: enable_alice,
            ),
            MenuItem("Выход", on_click_exit),
        ),
    )
    tray.run()


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


class splash(tk.Tk):
    """Класс сплеш-арта вызываемый при запуске."""

    def __init__(self):
        key_listener_thread = threading.Thread(target=self.key_checker, daemon=True)
        key_listener_thread.start()

        tk.Tk.__init__(self)
        # disable the window bar
        self.overrideredirect(True)
        # set trasparency and make the window stay on top
        self.attributes("-transparentcolor", "gray8", "-topmost", True)
        # set the background image
        self.psg = tk.PhotoImage(
            file=os.path.join(os.path.dirname(__file__), "data/splash.png")
        )
        self.label = tk.Label(self, bg="gray8", image=self.psg)
        self.label.pack()
        # move the window to center
        self.eval("tk::PlaceWindow . Center")
        self.leave_splash()

    def leave_splash(self):
        if choice_was_made_flag.is_set():
            self.destroy()
        else:
            self.after(500, self.leave_splash)

    def on_press(self, key):
        global enable_alice
        try:
            key_pressed = key.char
            if key_pressed == "1":
                enable_alice = False
                choice_was_made_flag.set()
            elif key_pressed == "2":
                enable_alice = True
                choice_was_made_flag.set()
        except:
            pass

    def key_checker(self):
        listener = keyboard.Listener(on_press=self.on_press)
        t = threading.Timer(timeout_splash, choice_was_made_flag.set)
        listener.start()
        t.start()
        choice_was_made_flag.wait()
        listener.stop()


if __name__ == "__main__":
    choice_was_made_flag = threading.Event()
    enable_alice = False
    spl = splash()
    spl.mainloop()

    exit_flag = threading.Event()

    daemon_thread_main = threading.Thread(target=mainfunc, daemon=True)
    daemon_thread_main.start()

    daemon_thread_tray = threading.Thread(target=trayfunc, daemon=True)
    daemon_thread_tray.start()

    exit_flag.wait()

    if enable_alice and not daemon_thread_main.is_alive():
        send_voice_msg()  # аккуратно со спамом, больше 10 в час не советуют (клиент апи тг)
        # pyrogram.Client должен быть в main thread'е, async и многопоточность
