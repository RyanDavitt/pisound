"""
File: raspgui.py
Author: RyanDavitt
Date: 06-22-2024

Description: Implements the primary means of utilizing PiSound with a Raspberry Pi-enabled touchscreen, the
primary goal of PiSound.

This program implements a more refined GUI of PiSound, leveraging methods from backend.py. The GUI consists of several
various elements that will be detailed here. At the top of the window is the mode bar, which will change depending on
the mode the program is in as well as give access to switching the modes, adding sounds, and quiting the program.
The rest (and majority) of the window is made of the Slots grid. Each slot can be filled by a sound, which will be used
for playing the sound, selecting for edit and movement, and deletion of the sound. There are three major "mode"
screens: Play Mode (Main Menu), Edit Mode, and Trash Mode.

From Play Mode, a selected slot will play the associated sound. Clicking the slot again will stop the sound if it is
still playing, and clicking another slot will interrupt and play its own sound (functionality of pressing the same slot
while it is playing is subject to change and most likely will eventually become a selectable mode feature). From Play
Mode, you may access the Add Sound function and Edit Mode.
"""
import tkinter as tk
import tkinter.ttk as ttk
from backend import *

num_slots_w = 7
num_slots_h = 4
window_w = 800
window_h = 480
root = tk.Tk()
slot_collection = [[None]*num_slots_h for i in range(num_slots_w)]
curr_timer = threading.Timer


class Slot:
    is_playing = False
    is_sound = False
    pos = -1
    timer = threading.Timer(0, stop_sound)
    button = None

    def __init__(self, x, y, pos, profile):
        self.pos = pos
        if self.pos == -1:
            self.button = ttk.Button(master=root, text="=Add Sound=", compound="center",
                                     command=lambda: self.add_sound())
            self.is_sound = False
        else:
            self.button = ttk.Button(master=root, text=profile[self.pos]["text"], compound="center",
                                     command=lambda: self.play_stop(profile))
            self.is_sound = True
        self.button.grid(row=y, column=x, sticky="nsew", padx=5, pady=5)

    def play_stop(self, profile):
        global curr_timer
        if not self.is_playing:
            switch_sounds()
            self.timer = play_sound(profile[self.pos])
            curr_timer = self.timer
        else:
            stop_sound(curr_timer)
        self.is_playing = not self.is_playing

    def add_sound(self):
        a_s_menu = tk.Menu(master=root, takefocus=True, title="Add Sound")

    def stop(self):
        if self.timer.is_alive():
            self.timer.cancel()
        self.is_playing = False


def switch_sounds():
    for i in slot_collection:
        for j in i:
            if j is not None:
                j.stop()


def init():
    global root

    cmd_prmpt_off()
    root.title("PiSound")
    # root.iconphoto()
    # window_h = root.winfo_screenheight()
    # window_w = root.winfo_screenwidth()

    # root.attributes("-fullscreen", True)
    root.geometry(f"{window_w}x{window_h}")
    root.rowconfigure(0, weight=1, minsize=75)
    for i in range(1, num_slots_h + 1):
        root.rowconfigure(i, weight=1, minsize=100)
    for i in range(num_slots_w):
        root.columnconfigure(i, weight=1, minsize=100)

    title = ttk.Label(master=root, text="PiSound", background="grey", anchor="center", justify="center", font="-family Courier -size 32 -weight bold")
    title.grid(row=0, column=int(num_slots_w/2) - 1, columnspan=3, sticky="nsew")
    quit_button = ttk.Button(master=root, text="Quit", command=end_program)
    quit_button.grid(row=0, column=0, sticky="nsew")


def populate(profile: list):
    num_item = 0
    #x = 0
    #y = 1
    if not profile:
        return
    for i in profile:
        new_slot = Slot(i["col"], i["row"] + 1, num_item, profile)
        slot_collection[i["col"]][i["row"]] = new_slot
        num_item = num_item + 1
        # x = x + 1
        # if x >= num_slots_w:
        #     x = 0
        #     y = y + 1

    for i in range(num_slots_w):
        for j in range(num_slots_h):
            if slot_collection[i][j] is None:
                new_slot = Slot(i, j + 1, -1, profile)
                slot_collection[i][j] = new_slot


def end_program():
    switch_sounds()
    root.destroy()
    exit()


def run():
    back_init()
    init()

    cmd_prmpt_off()
    profile = get_profile()
    populate(profile)

    root.mainloop()


if __name__ == "__main__":
    run()
