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
mode_text = ttk.Label
mode = tk.StringVar(master=root, value="Play Mode")

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
    this_profile: dict

    def __init__(self, x, y, pos, profile):
        self.pos = pos
        if self.pos == -1:  # "=Add Sound=" button (no edit mode on SoundWindow)
            self.button = ttk.Button(master=root, text="=Add Sound=", compound="center",
                                     command=lambda: SoundWindow(self, False))
            self.is_sound = False
        elif self.pos < -1:  # Menu button (changes to play (-2), edit(-3), or trash (-4) mode)
            self.update_menu_button()
        else:  # Play button (connects to a profile and plays a sound when pressed)
            self.button = ttk.Button(master=root, text=profile[self.pos]["text"], compound="center",
                                     command=self.play_stop)
            self.is_sound = True
            self.this_profile = profile[pos]
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

    def update_play_button(self):
        # self.button.destroy()
        # self.button = ttk.Button(master=root, text=profile[self.pos]["text"], compound="center",
        #                          command=lambda: self.play_stop(profile))
        self.button.config(text=self.this_profile["text"], command=self.play_stop)
        # self.button.grid(row=(self.y + 1), column=self.x, sticky="nsew", padx=5, pady=5)
        self.is_sound = True

    def update_menu_button(self, new_pos=None):
        if new_pos is not None:
            self.pos = new_pos

        if self.button is None:  # No button init yet
            match self.pos:
                case -2:
                    self.button = ttk.Button(master=root, text="Play Mode", compound="center",
                                             command=lambda: play_populate())
                case -3:
                    self.button = ttk.Button(master=root, text="Edit Mode", compound="center",
                                             command=lambda: edit_populate())
                case -4:
                    self.button = ttk.Button(master=root, text="Trash Mode", compound="center",
                                             command=lambda: play_populate())
        else:
            match self.pos:
                case -2:
                    self.button.config(text="Play Mode", command=lambda: play_populate())
                case -3:
                    self.button.config(text="Edit Mode", command=lambda: edit_populate())
                case -4:
                    self.button.config(text="Trash Mode", command=lambda: play_populate())

    def manual_update_button(self, text: str="", funct: Callable=None, state="", args=()):
        if text != "":
            self.button.config(text=text)
        if funct is not None:
            self.button.config(command=lambda: funct(*args))
        if state != "":
            self.button.config(state=state)

    def play_stop(self, test_profile: dict = None):
        global curr_timer

        if not self.is_sound:
            return

        if self.pos == -1:
            if not self.is_playing:
                if test_profile is None:
                    self.timer = play_sound(self.this_profile)
                else:
                    self.timer = play_sound(test_profile)
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
            if test_profile is None:
                self.timer = play_sound(self.this_profile)
            else:
                self.timer = play_sound(test_profile)
            curr_timer = self.timer
        else:
            stop_sound(curr_timer)
        self.is_playing = not self.is_playing

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
        if edit_mode:
            self.a_s_menu.title("Edit Sound")
        else:
            self.a_s_menu.title("Add Sound")
        self.a_s_menu.focus()
        top_frm = ttk.Frame(master=self.a_s_menu)
        if edit_mode:
            main_label = ttk.Label(master=top_frm, text="Edit Sound", anchor="center", justify="center",
                                   font="-family Courier -size 24 -weight bold")
        else:
            main_label = ttk.Label(master=top_frm, text="Add Sound", anchor="center", justify="center",
                                   font="-family Courier -size 24 -weight bold")
        discard_button = ttk.Button(master=top_frm, text="Discard", command=self.discard)
        save_button = ttk.Button(master=top_frm, text="Save and Exit", command=lambda: self.save(edit_mode))
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
        # Edit mode re-selects correct sound option
        if edit_mode:
            options = soundopts.get()
            ind = options.index(slot.this_profile["sound"])
            if ind >= 0:
                self.sound.selection_set(ind)
        ttk.Label(master=opts_frm, text="Image File Select (optional):", justify="center").grid(row=1, column=0)
        imgopts = tk.Variable(master=opts_frm, value=os.listdir(os.path.join("imgs")))
        self.img = tk.Listbox(master=opts_frm, activestyle="dotbox", selectmode="single",
                              listvariable=imgopts, height=3)
        self.img.grid(row=1, column=1, padx=self.padding, pady=self.padding)
        # Edit mode re-selects correct image option (NOT YET IMPLEMENTED)
        # if edit_mode:
        #     options = imgopts.get()
        #     ind = options.index(slot.this_profile["img"])
        #     if ind >= 0:
        #         self.img.selection_set(ind)
        ttk.Label(master=opts_frm, text="Set Sound Name:", justify="center").grid(row=2, column=0)
        self.text = tk.StringVar(master=opts_frm, name="Sound Name")
        # Edit mode resets to correct name
        if edit_mode:
            self.text.set(slot.this_profile["text"])
        ttk.Entry(master=opts_frm, justify="left", textvariable=self.text).grid(row=2, column=1, padx=self.padding,
                                                                                pady=self.padding)
        opts_frm.pack()

        # Volume Set (packed)
        ttk.Label(master=self.a_s_menu, text="Set Volume:", justify="center").pack()
        self.vol = tk.IntVar(master=self.a_s_menu, name="Volume")
        ttk.LabeledScale(master=self.a_s_menu, to=100, from_=0, variable=self.vol).pack_configure(padx=self.padding,
                                                                                                  pady=self.padding)
        self.vol.set(25)
        if edit_mode:
            self.vol.set(int(float(slot.this_profile["volume"]) * 100))

        # Bounds Frame (gridded)(Start Set, End Set)
        bound_frm = ttk.Frame(master=self.a_s_menu)
        valid_end = self.a_s_menu.register(self.validate_end)
        self.start = tk.DoubleVar(master=self.a_s_menu, value=0.0)
        self.end = tk.DoubleVar(master=self.a_s_menu, value=0.0)
        if edit_mode:
            self.start.set(slot.this_profile["start"])
            self.end.set(slot.this_profile["end"])
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

    def save(self, edit_mode):
        try:
            file = self.sound.selection_get()
        except tk.TclError:
            self.a_s_menu.destroy()
            return
        if edit_mode:
            edit_sound(self.change_slot.pos, sound=file, text=self.text.get(), vol=self.vol.get(),
                       start=self.start.get(), end=self.end.get(), row=self.change_slot.y, col=self.change_slot.x)
        else:
            self.change_slot.pos, profile = add_sound(sound=file, text=self.text.get(), vol=self.vol.get(),
                                                      start=self.start.get(), end=self.end.get(),
                                                      row=self.change_slot.y, col=self.change_slot.x)
        self.change_slot.update_play_button()
        self.a_s_menu.destroy()

    def test_play(self):  # Fix to match same function as start/stop of normal slots
        try:
            test_profile = {"sound": self.sound.selection_get(), "text": self.text.get(),
                             "img": self.img.selection_get(), "volume": self.vol.get() / 100, "start": self.start.get(),
                             "end": self.end.get(), "row": -1, "col": -1}
        except tk.TclError:
            return

        self.change_slot.play_stop(test_profile=test_profile)

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
menu_slots: list[Slot] = []


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

    title = ttk.Label(master=root, text="PiSound", background="grey", anchor="center", justify="center",
                      font="-family Courier -size 32 -weight bold")
    title.grid(row=0, column=int(num_slots_w/2) - 1, columnspan=3, sticky="nsew")
    mode_type = ttk.Label(master=root, textvariable=mode, foreground="green", anchor="center", justify="center",
                          font="-family Courier -size 14 -weight bold")
    mode_type.grid(row=0, column=1, sticky="nsew")
    quit_button = ttk.Button(master=root, text="Quit", command=end_program)
    quit_button.grid(row=0, column=0, sticky="nsew")


    return mode_type


def init_populate():
    profile = get_profile()
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

    new_slot = Slot(num_slots_w - 2, -1, -3, profile) # Set Edit Mode button
    menu_slots.append(new_slot)
    new_slot = Slot(num_slots_w - 1, -1, -4, profile) # Set Trash Mode button
    menu_slots.append(new_slot)


def play_populate():
    profile = get_profile()
    num_item = 0
    coords = []
    if profile:
        for i in profile:
            coords.append([i["col"], i["row"]])
            new_slot = slot_collection[coords[num_item][0]][coords[num_item][1]]
            new_slot.manual_update_button(text=i["text"], funct=new_slot.play_stop, state="normal",
                                          args=(profile,))
            num_item = num_item + 1

    for i in range(num_slots_w):
        for j in range(num_slots_h):
            if [i, j] not in coords:
                new_slot = slot_collection[i][j]
                new_slot.manual_update_button(state="normal")

    menu_slots[0].update_menu_button(new_pos=-3)
    menu_slots[1].update_menu_button(new_pos=-4)
    mode.set("Play Mode")
    mode_text.config(foreground="green")


def edit_populate():
    profile = get_profile()
    num_item = 0
    coords = []
    if profile:
        for i in profile:
            coords.append([i["col"], i["row"]])
            new_slot = slot_collection[coords[num_item][0]][coords[num_item][1]]
            new_slot.manual_update_button(funct=SoundWindow, args=(new_slot, True))
            num_item = num_item + 1

    for i in range(num_slots_w):
        for j in range(num_slots_h):
            if [i, j] not in coords:
                new_slot = slot_collection[i][j]
                new_slot.manual_update_button(state="disabled")

    menu_slots[0].update_menu_button(new_pos=-2)
    menu_slots[1].update_menu_button(new_pos=-4)
    mode.set("Edit Mode")
    mode_text.config(foreground="orange")


def end_program():
    switch_sounds()
    root.destroy()
    exit()


def run():
    global mode_text

    back_init()
    mode_text = init()

    cmd_prmpt_off()
    init_populate()

    root.mainloop()


if __name__ == "__main__":
    run()
