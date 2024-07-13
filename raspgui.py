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
from typing import Callable
import tkinter as tk
import tkinter.ttk as ttk
import os
import platform
from backend import *

num_slots_w = 7
num_slots_h = 4
window_w = 800
window_h = 480
root = tk.Tk()

curr_timer = threading.Timer


class Slot:
    is_playing = False
    is_sound = False
    pos = -1
    timer = threading.Timer
    button = None
    x = -1
    y = -1
    dur = tk.DoubleVar(value=0.0)
    dur_timer = None
    timer_run = False

    def __init__(self, x, y, pos, profile):
        self.pos = pos
        if self.pos == -1: # "=Add Sound=" button (no edit mode on SoundWindow)
            self.button = ttk.Button(master=root, text="=Add Sound=", compound="center",
                                     command=lambda: SoundWindow(self, False))
            self.is_sound = False
        else:
            self.button = ttk.Button(master=root, text=profile[self.pos]["text"], compound="center",
                                     command=lambda: self.play_stop(profile))
            self.is_sound = True
        self.button.grid(row=(y + 1), column=x, sticky="nsew", padx=5, pady=5)
        self.x = x
        self.y = y
        self.timer = threading.Timer(0.0, self.play_stop)

    def timer_update(self, timer: threading.Timer):
        while self.timer_run:
            self.dur.set(round(self.dur.get() + 0.1, 1))
            if timer.finished.is_set():
                self.timer_run = False
            time.sleep(0.1)

    def timer_init(self):
        self.dur_timer = threading.Thread(target=self.timer_update, args=(curr_timer,))
        self.dur_timer.daemon = True

    def manual_update_button(self, text: str, funct: Callable, args=()):
        self.button.config(text=text, command=lambda: funct(*args))

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

    def update_play_button(self, profile):
        # self.button.destroy()
        # self.button = ttk.Button(master=root, text=profile[self.pos]["text"], compound="center",
        #                          command=lambda: self.play_stop(profile))
        self.button.config(text=profile[self.pos]["text"], command=lambda: self.play_stop(profile))
        # self.button.grid(row=(self.y + 1), column=self.x, sticky="nsew", padx=5, pady=5)
        self.is_sound = True

    def stop(self):
        if self.timer.is_alive():
            self.timer.cancel()
        self.is_playing = False


class SoundWindow:
    a_s_menu = tk.Toplevel
    change_slot = Slot
    padding = 2
    sound = tk.Listbox
    img = tk.Listbox
    text = tk.StringVar
    vol = tk.IntVar
    start = tk.DoubleVar
    end = tk.DoubleVar

    def __init__(self, slot: Slot, edit_mode: bool):
        self.a_s_menu = tk.Toplevel(master=root)
        self.change_slot = slot
        self.change_slot.is_sound = True  # Temporarily is_sound = True to allow for test-playing
        self.a_s_menu.geometry(f"{int(window_w / 1.5)}x{int(window_h / 1.25)}")
        self.a_s_menu.title("Add Sound")
        self.a_s_menu.focus()
        top_frm = ttk.Frame(master=self.a_s_menu)
        main_label = ttk.Label(master=top_frm, text="Add Sound", anchor="center", justify="center",
                               font="-family Courier -size 24 -weight bold")
        discard_button = ttk.Button(master=top_frm, text="Discard", command=self.discard)
        save_button = ttk.Button(master=top_frm, text="Save and Exit", command=self.save)
        top_frm.pack()
        main_label.pack_configure(side="top")
        discard_button.pack_configure(side="left")
        save_button.pack_configure(side="right")

        # Options frame (gridded)(Sound Sel, Image Sel, Name Set)
        opts_frm = ttk.Frame(master=self.a_s_menu)
        ttk.Label(master=opts_frm, text="Sound File Select:", justify="center").grid(row=0, column=0)
        soundopts = tk.Variable(master=opts_frm, value=os.listdir(os.path.join("sounds")))
        self.sound = tk.Listbox(master=opts_frm, activestyle="dotbox", selectmode="single",
                                listvariable=soundopts, height=3)
        self.sound.grid(row=0, column=1, padx=self.padding, pady=self.padding)
        ttk.Label(master=opts_frm, text="Image File Select (optional):", justify="center").grid(row=1, column=0)
        imgopts = tk.Variable(master=opts_frm, value=os.listdir(os.path.join("imgs")))
        self.img = tk.Listbox(master=opts_frm, activestyle="dotbox", selectmode="single",
                              listvariable=imgopts, height=3)
        self.img.grid(row=1, column=1, padx=self.padding, pady=self.padding)
        ttk.Label(master=opts_frm, text="Set Sound Name:", justify="center").grid(row=2, column=0)
        self.text = tk.StringVar(master=opts_frm, name="Sound Name")
        ttk.Entry(master=opts_frm, justify="left", textvariable=self.text).grid(row=2, column=1, padx=self.padding,
                                                                                pady=self.padding)
        opts_frm.pack()

        valid_end = self.a_s_menu.register(self.validate_end)
        # Volume Set (packed)
        ttk.Label(master=self.a_s_menu, text="Set Volume:", justify="center").pack()
        self.vol = tk.IntVar(master=self.a_s_menu, name="Volume")
        ttk.LabeledScale(master=self.a_s_menu, to=100, from_=0, variable=self.vol).pack_configure(padx=self.padding,
                                                                                                  pady=self.padding)
        self.vol.set(25)

        # Bounds Frame (gridded)(Start Set, End Set)
        bound_frm = ttk.Frame(master=self.a_s_menu)
        self.start = tk.DoubleVar(master=self.a_s_menu, value=0.0)
        self.end = tk.DoubleVar(master=self.a_s_menu, value=0.0)
        ttk.Label(master=bound_frm, text="Set Start Second Value:", justify="right").grid(row=0, column=0)
        ttk.Label(master=bound_frm, text="Set End Second Value:", justify="right").grid(row=1, column=0)
        ttk.Entry(master=bound_frm, textvariable=self.start).grid(row=0, column=1)
        ttk.Entry(master=bound_frm, textvariable=self.end, validate="key",
                  validatecommand=(valid_end, "%P")).grid(row=1, column=1)
        bound_frm.pack()

        ttk.Button(master=self.a_s_menu, text="Test Play/Stop Sound", command=self.test_play).pack()
        ttk.Label(master=self.a_s_menu, textvariable=self.change_slot.dur).pack()

    def discard(self):
        self.change_slot.is_sound = False
        self.a_s_menu.destroy()

    def save(self):
        try:
            file = self.sound.selection_get()
        except tk.TclError:
            self.a_s_menu.destroy()
            return

        self.change_slot.pos, profile = add_sound(sound=file, text=self.text.get(), vol=self.vol.get(),
                                                  start=self.start.get(), end=self.end.get(), row=self.change_slot.y,
                                                  col=self.change_slot.x)
        self.change_slot.update_play_button(profile)
        self.a_s_menu.destroy()

    def test_play(self):  # Fix to match same function as start/stop of normal slots
        try:
            test_profile = [{"sound": self.sound.selection_get(), "text": self.text.get(),
                             "img": self.img.selection_get(), "volume": self.vol.get() / 100, "start": self.start.get(),
                             "end": self.end.get(), "row": -1, "col": -1}]
        except tk.TclError:
            return

        self.change_slot.play_stop(test_profile)

    def validate_end(self, num: str):
        if num == "":
            return True
        decim = num.find(".")
        if (num[0: decim].isdigit() or 0 == decim) and (
                num[decim + 1:].isdigit() or len(num) - 1 == decim) or num.isdigit():
            try:
                if float(num) > update_bounds(os.path.join("sounds", self.sound.selection_get())):
                    return False
                else:
                    return True
            except tk.TclError:
                return False
        else:
            return False


# Global slot collection 2D list
slot_collection = [[Slot for i in range(num_slots_h)] for j in range(num_slots_w)]


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

    if platform.system() == "Linux":
        root.attributes("-fullscreen", True)

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


def init_populate(profile: list):
    num_item = 0
    coords = []
    #x = 0
    #y = 1
    if profile:
        for i in profile:
            coords.append([i["col"], i["row"]])
            new_slot = Slot(coords[num_item][0], coords[num_item][1], num_item, profile)
            slot_collection[coords[num_item][0]][coords[num_item][1]] = new_slot
            num_item = num_item + 1
            # x = x + 1
            # if x >= num_slots_w:
            #     x = 0
            #     y = y + 1

    for i in range(num_slots_w):
        for j in range(num_slots_h):
            if [i, j] not in coords:
                new_slot = Slot(i, j, -1, profile)
                slot_collection[i][j] = new_slot


def play_populate(profile: list):
    num_item = 0
    coords = []
    if profile:
        for i in profile:
            coords.append([i["col"], i["row"]])
            new_slot = slot_collection[coords[num_item][0]][coords[num_item][1]]
            new_slot.manual_update_button(new_slot, i["text"], new_slot.play_stop, args=(new_slot, profile))
            num_item = num_item + 1

    for i in range(num_slots_w):
        for j in range(num_slots_h):
            if [i, j] not in coords:
                new_slot = slot_collection[i][j]



def end_program():
    switch_sounds()
    root.destroy()
    exit()


def run():
    back_init()
    init()

    cmd_prmpt_off()
    profile = get_profile()
    init_populate(profile)

    root.mainloop()


if __name__ == "__main__":
    run()
