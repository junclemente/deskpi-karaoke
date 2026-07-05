import logging
import tkinter as tk
import threading

logger = logging.getLogger(__name__)


def show_info(message, title="PiKaraoke", duration=3, x=400, y=200):
    def popup():
        try:
            root = tk.Tk()
            root.title(title)
            root.geometry(f"+{x}+{y}")
            root.attributes("-topmost", True)
            root.resizable(False, False)
            tk.Label(root, text=message, padx=20, pady=20, font=("Arial", 12)).pack()
            root.after(duration * 1000, root.destroy)
            root.mainloop()
        except Exception as e:
            logger.info("%s (GUI error: %s)", message, e)

    threading.Thread(target=popup).start()


def show_error(message, title="PiKaraoke Error", x=400, y=200):
    def popup():
        try:
            root = tk.Tk()
            root.title(title)
            root.geometry(f"+{x}+{y}")
            root.attributes("-topmost", True)
            root.resizable(False, False)
            tk.Label(
                root, text=message, padx=20, pady=20, font=("Arial", 12), fg="red"
            ).pack()
            root.mainloop()
        except Exception as e:
            logger.error("%s (GUI error: %s)", message, e)

    threading.Thread(target=popup).start()
