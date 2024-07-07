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
import time
import tkinter as tk
import tkinter.ttk as ttk
import os
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
    x = -1
    y = -1
    dur = tk.DoubleVar(value=0.0)
    dur_timer = None
    timer_run = False

    def __init__(self, x, y, pos, profile):
        self.pos = pos
        if self.pos == -1:
            self.button = ttk.Button(master=root, text="=Add Sound=", compound="center",
                                     command=self.gui_add_sound)
            self.is_sound = False
        else:
            self.button = ttk.Button(master=root, text=profile[self.pos]["text"], compound="center",
                                     command=lambda: self.play_stop(profile))
            self.is_sound = True
        self.button.grid(row=(y + 1), column=x, sticky="nsew", padx=5, pady=5)
        self.x = x
        self.y = y

    def timer_update(self, timer: threading.Timer):
        while self.timer_run:
            self.dur.set(round(self.dur.get() + 0.1, 1))
            if timer.finished.is_set():
                self.timer_run = False
            time.sleep(0.1)

    def timer_init(self):
        self.dur_timer = threading.Thread(target=self.timer_update, args=(curr_timer,))
        self.dur_timer.daemon = True

    def play_stop(self, profile):
        global curr_timer

        if not self.is_sound:
            return

        if self.pos == -1:
            if not self.is_playing:
                self.timer = play_sound(profile[0])
                curr_timer = self.timer
                self.dur.set(0)
                self.timer_init()
                self.timer_run = True
                self.dur_timer.start()
            else:
                stop_sound(curr_timer)
                self.timer_run = False
            self.is_playing = not self.is_playing
            return

        if not self.is_playing:
            switch_sounds()
            self.timer = play_sound(profile[self.pos])
            curr_timer = self.timer
        else:
            stop_sound(curr_timer)
        self.is_playing = not self.is_playing

    def update_button(self, profile):
        self.button.destroy()
        self.button = ttk.Button(master=root, text=profile[self.pos]["text"], compound="center",
                                 command=lambda: self.play_stop(profile))
        self.button.grid(row=(self.y + 1), column=self.x, sticky="nsew", padx=5, pady=5)
        self.is_sound = True

    def gui_add_sound(self):  # Makes an add sound window
        a_s_menu = tk.Toplevel(master=root)
        start = tk.DoubleVar(master=a_s_menu, value=0.0)
        end = tk.DoubleVar(master=a_s_menu, value=0.0)

        def discard():
            self.is_sound = False
            a_s_menu.destroy()

        def save():
            try:
                file = sound.selection_get()
            except tk.TclError:
                a_s_menu.destroy()
                return

            self.pos, profile = add_sound(sound=file, text=text.get(), vol=vol.get(), start=start.get(), end=end.get(),
                                          row=self.y, col=self.x)
            self.update_button(profile)
            a_s_menu.destroy()

        def test_play():    # Fix to match same function as start/stop of normal slots
            try:
                test_profile = [{"sound": sound.selection_get(), "text": text.get(),
                                 "img": img.selection_get(), "volume": vol.get()/100, "start": start.get(),
                                 "end": end.get(), "row": -1, "col": -1}]
            except tk.TclError:
                return

            self.play_stop(test_profile)

        padding = 2

        # Init (packed)
        self.is_sound = True # Temporarily is_sound = True to allow for test-playing
        a_s_menu.geometry(f"{int(window_w / 1.5)}x{int(window_h / 1.25)}")
        a_s_menu.title("Add Sound")
        a_s_menu.focus()
        top_frm = ttk.Frame(master=a_s_menu)
        main_label = ttk.Label(master=top_frm, text="Add Sound", anchor="center", justify="center",
                               font="-family Courier -size 24 -weight bold")
        discard_button = ttk.Button(master=top_frm, text="Discard", command=discard)
        save_button = ttk.Button(master=top_frm, text="Save and Exit", command=save)
        top_frm.pack()
        main_label.pack_configure(side="top")
        discard_button.pack_configure(side="left")
        save_button.pack_configure(side="right")

        # Options frame (gridded)(Sound Sel, Image Sel, Name Set)
        opts_frm = ttk.Frame(master=a_s_menu)
        ttk.Label(master=opts_frm, text="Sound File Select:", justify="center").grid(row=0, column=0)
        soundopts = tk.Variable(master=opts_frm, value=os.listdir(os.path.join("sounds")))
        sound = tk.Listbox(master=opts_frm,  activestyle="dotbox", selectmode="single",
                           listvariable=soundopts, height=3)
        sound.grid(row=0, column=1, padx=padding, pady=padding)
        ttk.Label(master=opts_frm, text="Image File Select (optional):", justify="center").grid(row=1, column=0)
        imgopts = tk.Variable(master=opts_frm, value=os.listdir(os.path.join("imgs")))
        img = tk.Listbox(master=opts_frm,  activestyle="dotbox", selectmode="single",
                         listvariable=imgopts, height=3)
        img.grid(row=1, column=1, padx=padding, pady=padding)
        ttk.Label(master=opts_frm, text="Set Sound Name:", justify="center").grid(row=2, column=0)
        text = tk.StringVar(master=opts_frm, name="Sound Name")
        ttk.Entry(master=opts_frm, justify="left", textvariable=text).grid(row=2, column=1, padx=padding, pady=padding)
        opts_frm.pack()

        def validate_end(num: str):
            if num == "":
                return True
            decim = num.find(".")
            if (num[0: decim].isdigit() or 0 == decim) and (num[decim + 1:].isdigit() or len(num) - 1 == decim) or num.isdigit():
                try:
                    if float(num) > update_bounds(os.path.join("sounds", sound.selection_get())):
                        return False
                    else:
                        return True
                except tk.TclError:
                    return False
            else:
                return False

        valid_end = a_s_menu.register(validate_end)
        # Volume Set (packed)
        ttk.Label(master=a_s_menu, text="Set Volume:", justify="center").pack()
        vol = tk.IntVar(master=a_s_menu, name="Volume")
        ttk.LabeledScale(master=a_s_menu, to=100, from_=0, variable=vol).pack_configure(padx=padding, pady=padding)
        vol.set(25)

        # Bounds Frame (gridded)(Start Set, End Set)
        bound_frm = ttk.Frame(master=a_s_menu)
        ttk.Label(master=bound_frm, text="Set Start Second Value:", justify="right").grid(row=0, column=0)
        ttk.Label(master=bound_frm, text="Set End Second Value:", justify="right").grid(row=1, column=0)
        ttk.Entry(master=bound_frm, textvariable=start).grid(row=0, column=1)
        ttk.Entry(master=bound_frm, textvariable=end, validate="key", validatecommand=(valid_end, "%P")).grid(row=1, column=1)
        bound_frm.pack()

        ttk.Button(master=a_s_menu, text="Test Play/Stop Sound", command=test_play).pack()
        ttk.Label(master=a_s_menu, textvariable=self.dur).pack()

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

    return title


def populate(profile: list):
    num_item = 0
    #x = 0
    #y = 1
    if not profile:
        return
    for i in profile:
        new_slot = Slot(i["col"], i["row"], num_item, profile)
        slot_collection[i["col"]][i["row"]] = new_slot
        num_item = num_item + 1
        # x = x + 1
        # if x >= num_slots_w:
        #     x = 0
        #     y = y + 1

    for i in range(num_slots_w):
        for j in range(num_slots_h):
            if slot_collection[i][j] is None:
                new_slot = Slot(i, j, -1, profile)
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
