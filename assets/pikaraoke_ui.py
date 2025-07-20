import tkinter as tk
import threading


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
            print(f"[INFO] {message} (GUI error: {e})")

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
            print(f"[ERROR] {message} (GUI error: {e})")

    threading.Thread(target=popup).start()
