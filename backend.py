"""
File: backend.py
Author: RyanDavitt
Date: 06-21-2024

Description: Implements the MVP as an operational program through the command prompt as an interface.

The backend is, as the filename suggests, the backend of the program, implementing all the behind the scenes with an
ugly interface (the command prompt). It is possible to run all basic functions of the PiSound program by running this
file and controlling through the command prompt, given that the global variable run_in_cmd remains True (other file's
functions, such as the GUI, that call on file must set run_in_cmd to False in order to not get stuck in the command
prompt inputs and loops that were built with said command prompt inputs in mind).
"""
import json
import pygame
import threading
import time
from pygame import mixer_music as mix
import pygame.mixer as mixer

#
# JSON format is: profile = [{"sound": "sounds/...", "text": "Name", "img": "imgs/...", "vol": 0.25, ", "start": 0.0,
#                             "end": 0.0, "row": 0, "col": 0}, {"sound":...}]
# Key descriptions: sound = sound filename (str type path, adjusted from "[file]" to "sounds/[file]")
#                   text = sound name to be displayed (str type)
#                   img = image to be displayed by GUI (str type path, adjusted from "[file]" to
#                         "imgs/[file]". Not implemented yet)
#                   vol = volume to play at. Inputted at percent (25, 62, ...),
#                         stored as decimal value (float type) of percent
#                   start = where to place playhead at sound playback start in seconds (float type)
#                   end = where to stop sound playback in seconds (float type)
#                   row = which row to place slot in GUI (int type, -1 is default for no GUI display)
#                   col = which column to place slot in GUI (int type, -1 is default for no GUI display)
# Test path: C:\Users\Ryan\PycharmProjects\RandomProjects\PiSound\sounds\Carl-spacito.mp3

run_in_cmd = True           # When False, indicates running with GUI. Avoid cmd prmpt inputs and input loops
file = "profile.json"
profile = []

default_vol = 25


def get_profile():
    return profile


def cmd_prmpt_off():
    global run_in_cmd

    run_in_cmd = False


def update_json():
    global profile
    fp = open(file, "w")
    json.dump(profile, fp)
    fp.close()


def add_sound(sound="", text="", vol=default_vol, start=0.0, end=0.0, row=-1, col=-1):
    if run_in_cmd:
        sound = input("Input sound filename: ")
        text = input("Input sound name: ")
        vol = input(f"Input sound volume (out of 100, default {default_vol}): ")
        start = input("Input start time (seconds, default 0.0): ")
        end = input("Input end time (seconds, default 0.0): ")

    if vol != "":
        vol = int(vol)
    else:
        vol = 50
    if start != "":
        start = float(start)
    else:
        start = 0.0
    if end != "":
        end = float(end)
    else:
        end = 0.0

    new_dict = {"sound": "sounds\\" + sound, "text": text, "volume": vol / 100, "start": start, "end": end, "row": row,
                "col": col}

    profile.append(new_dict)
    update_json()

    return len(profile) - 1, profile


def update_bounds(filename):
    return mixer.Sound(filename).get_length()


def play_sound(sel: dict):
    if run_in_cmd:
        print("Now playing " + sel["text"] + "...")

    mix.set_volume(float(sel["volume"]))
    mix.load(sel["sound"])
    mix.play()
    mix.set_pos(float(sel["start"]))
    if float(sel["end"]) > 0:
        timer = threading.Timer(float(sel["end"]) - float(sel["start"]), lambda: stop_sound(timer))
        timer.start()
    else:
        timer = threading.Timer(0, stop_sound)
    return timer


def stop_sound(timer: threading.Timer):
    mix.stop()
    if timer is not None:
        timer.cancel()


def edit_sound(num: int, sound="", text="", vol=-1, start=-1, end=-1, row=-1, col=-1):
    global profile
    sel = profile[num]
    cont_edit = True

    while cont_edit:
        if run_in_cmd:
            sound = input("Input sound filename (leave blank for no change): ")
            text = input("Input sound name (leave blank for no change): ")
            vol = input("Input sound volume (out of 100, leave blank for no change): ")
            start = input("Input start time (seconds, leave blank for no change): ")
            end = input("Input end time (seconds, leave blank for no change): ")

        if sound != "":
            sel.update({"sound": "sounds\\" + sound})
        if text != "":
            sel.update({"text": text})
        if vol != "" and vol != -1:
            sel.update({"volume": int(vol) / 100})
        if start != "" and start != -1:
            sel.update({"start": float(start)})
        if end != "" and end != -1:
            sel.update({"end": float(end)})
        if row != -1:
            sel.update({"row": row})
        if col != -1:
            sel.update({"col": col})

        if run_in_cmd:
            while 1:
                cmd = input("Play Changes (P), Save (S), Redo Changes (R), or Discard Changes (D): ").upper()

                match cmd:
                    case "P":
                        play_sound(sel)
                    case "S":
                        cont_edit = False
                        break
                    case "R":
                        break
                    case "D":
                        return
                    case _:
                        print("No valid command detected...")

        else:
            cont_edit = False

    profile[num] = sel
    update_json()


def delete_sound(num: int):
    global profile

    if run_in_cmd:
        cmd = input("Are you sure you want to delete \"" + profile[num]["text"] + "\" [Y/N]? ").upper()
    else:
        cmd = "Y"

    match cmd:
        case "Y":
            last_text = profile[num]["text"]
            profile.remove(profile[num])
            update_json()
            if run_in_cmd:
                print(last_text + "has been deleted.")
        case _:
            if run_in_cmd:
                print(profile[num]["text"] + "will not be deleted.")


def back_init():
    global profile
    pygame.init()
    is_new_profile = False

    try:
        fp = open(file, "r")
    except OSError:
        is_new_profile = True
        fp = open(file, "x")
        fp.close()

    if is_new_profile:
        profile = []
    else:
        try:
            profile = json.load(fp)
        except OSError:
            profile = []
        fp.close()


def back_main():                        # Used as a model for how the GUI should operate.
    global profile
    is_running = True
    mode = "M"                          # Modes: "M": Main, "E": Edit Mode, "T": Trash Mode
    timer = threading.Timer(0, stop_sound)

    if run_in_cmd:
        back_init()

    while is_running:
        # Runs /every/ time to keep values updated
        keys = len(profile)

        match mode:                     # Mode selector
            # Edit Mode
            case "E":
                if run_in_cmd:
                    cmd = input("Select sound to edit (numeric), return to Play Mode (P), enter Trash Mode (T): ")\
                                .upper()
                else:
                    cmd = "P"

                if cmd.isdigit():
                    num = int(cmd)
                    if num < keys:
                        edit_sound(num)
                    else:
                        if run_in_cmd:
                            print("No such sound exists...")
                    continue

                match cmd:              # Mode changer
                    case "P":
                        mode = "M"
                    case "T":
                        mode = "T"
                    case _:
                        if run_in_cmd:
                            print("No valid command detected...")

            # Trash Mode
            case "T":
                if run_in_cmd:
                    cmd = input("Select sound to delete (numeric), return to Edit Mode (E), enter Play Mode (P): ")\
                                .upper()
                else:
                    cmd = "E"

                if cmd.isdigit():
                    num = int(cmd)
                    if num < keys:
                        delete_sound(num)
                    else:
                        if run_in_cmd:
                            print("No such sound exists...")
                    continue

                match cmd:              # Mode changer
                    case "E":
                        mode = "E"
                    case "P":
                        mode = "M"
                    case _:
                        if run_in_cmd:
                            print("No valid command detected...")

            case _:  # Main (Play) Mode
                if run_in_cmd:
                    cmd = input("Select sound to play (numeric), stop playing sound (S), enter Edit Mode (E)," +
                                "Add Sound(A), or Quit (Q): ").upper()
                else:
                    cmd = "0"

                if cmd.isdigit():
                    num = int(cmd)
                    if num < keys:
                        sel = profile[num]
                        timer = play_sound(sel)
                    else:
                        if run_in_cmd:
                            print("No such sound exists...")
                    continue

                match cmd:
                    case "S":           # Stop playing sound
                        stop_sound(timer)
                    case "A":           # Add new sound
                        add_sound()
                    case "E":           # Mode changer
                        mode = "E"
                    case "Q":           # Quit
                        is_running = False
                        if run_in_cmd:
                            print("See ya!")
                    case _:
                        if run_in_cmd:
                            print("No valid command detected...")


if __name__ == "__main__":
    back_main()
