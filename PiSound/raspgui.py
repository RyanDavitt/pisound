import tkinter as tk
import tkinter.ttk as ttk
from backend import *

num_slots_w = 7
num_slots_h = 9
window_w = 800
window_h = 480
root = tk.Tk()
slot_collection = []


class Slot:
    def __init__(self, x, y, pos, profile):
        self.button = ttk.Button(master=root, text=profile[pos]["text"],
                                command=lambda: play_sound(profile[pos]))
        self.button.grid(row=y, column=x, sticky="nsew", padx=5, pady=5)


def setup():
    global root

    cmd_prmpt_off()
    root.title("PiSound")
    # root.iconphoto()
    # window_h = root.winfo_screenheight()
    # window_w = root.winfo_screenwidth()

    # root.attributes("-fullscreen", True)
    root.geometry(f"{window_w}x{window_h}")
    root.rowconfigure(0, weight=2, minsize=100)
    for i in range(1, num_slots_h + 1):
        root.rowconfigure(i, weight=1, minsize=100)
    for i in range(num_slots_w):
        root.columnconfigure(i, weight=1, minsize=100)

    title = ttk.Label(master=root, text="PiSound", background="grey", anchor="center", justify="center", font="-family Courier -size 32 -weight bold")
    title.grid(row=0, column=int(num_slots_w/2), sticky="nsew")
    quit_button = ttk.Button(master=root, text="Quit", command=root.destroy)
    quit_button.grid(row=0, column=0, sticky="nsew")


def populate(profile: list):
    num_item = 0
    x = 0
    y = 1
    if not profile:
        return
    for i in profile:
        new_slot = Slot(x, y, num_item, profile)
        slot_collection.append(new_slot)
        num_item = num_item + 1
        x = x + 1
        if x >= num_slots_w:
            x = 0
            y = y + 1



def run():
    setup()
    back_setup()
    cmd_prmpt_off()
    profile = get_profile()
    populate(profile)

    root.mainloop()


if __name__ == "__main__":
    run()