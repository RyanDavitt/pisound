import json
import pygame
import threading
import time
from pygame import mixer_music as mix
from raspgui import run

run_in_cmd = True
file = "profile.json"
profile = []
# JSON format is: profile = [{"sound": "sounds/...", "text": "Name", "img": "imgs/...", "vol": 100, ", "start": 0, "end": 0}, {"sound":...}]
# Test path: C:\Users\Ryan\PycharmProjects\RandomProjects\PiSound\sounds\Carl-spacito.mp3


def update_json():
    global profile
    fp = open(file, "w")
    json.dump(profile, fp)
    fp.close()


def add_sound():
    if run_in_cmd:
        sound = input("Input sound path: ")
        text = input("Input sound name: ")
        vol = input("Input sound volume (out of 100): ")
        start = input("Input start time (seconds): ")
        end = input("Input end time (seconds): ")

    new_dict = {"sound": sound, "text": text, "volume": vol, "start": start, "end": end}

    return new_dict


def play_sound(sel):
    if run_in_cmd:
        print("Now playing " + sel["text"] + "...")

    mix.set_volume(int(sel["volume"]) / 100)
    mix.load(sel["sound"])
    mix.play()
    mix.set_pos(float(sel["start"]))
    if float(sel["end"]) > 0:
        threading.Timer(float(sel["end"]) - float(sel["start"]), stop_sound).start()


def stop_sound():
    mix.stop()


def edit_sound(num):
    global profile
    sel = profile[num]
    cont_edit = True

    while cont_edit:
        if run_in_cmd:
            sound = input("Input sound path (leave blank for no change): ")
            text = input("Input sound name (leave blank for no change): ")
            vol = input("Input sound volume (out of 100, leave blank for no change): ")
            start = input("Input start time (seconds, leave blank for no change): ")
            end = input("Input end time (seconds, leave blank for no change): ")

        if sound != "":
            sel.update({"sound": sound})
        if text != "":
            sel.update({"text": text})
        if vol != "":
            sel.update({"volume": int(vol)})
        if start != "":
            sel.update({"start": float(start)})
        if end != "":
            sel.update({"end": float(end)})

        while 1:
            if run_in_cmd:
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

    profile[num] = sel
    update_json()


def delete_sound(num):
    global profile

    if run_in_cmd:
        cmd = input("Are you sure you want to delete \"" + profile[num]["text"] + "\" [Y/N]? ")
    else:
        cmd = "N"

    match cmd:
        case "Y":
            last_text = profile[num]["text"]
            profile.remove(profile[num])
            update_json()
            print(last_text + "has been deleted.")
        case _:
            print(profile[num]["text"] + "will not be deleted.")


def main():
    global profile
    pygame.init()
    is_new_profile = False

    try:
        fp = open(file, "r")
    except:
        is_new_profile = True
        fp = open(file, "x")
        fp.close()

    if is_new_profile:
        profile = []
    else:
        try:
            profile = json.load(fp)
        except:
            profile = []
        fp.close()

    keys = len(profile)

    is_running = True
    mode = "M"                          # Modes: "M": Main, "E": Edit Mode, "T": Trash Mode

    while is_running:
        # Runs /every/ time to keep values updated
        keys = len(profile)

        match mode:                     # Mode selector
            # Edit Mode
            case "E":
                if run_in_cmd:
                    cmd = input("Select sound to edit (numeric), return to Play Mode (P), enter Trash Mode (T): ")
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

                cmd = cmd.upper()

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
                    cmd = input("Select sound to delete (numeric), return to Edit Mode (E), enter Play Mode (P): ")
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

                cmd = cmd.upper()

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
                    cmd = input("Select sound to play (numeric), stop playing sound (S), enter Edit Mode (E), Add Sound\
(A), or Quit (Q): ")
                else:
                    cmd = "0"

                if cmd.isdigit():
                    num = int(cmd)
                    if num < keys:
                        sel = profile[num]
                        play_sound(sel)
                    else:
                        if run_in_cmd:
                            print("No such sound exists...")
                    continue

                cmd = cmd.upper()

                match cmd:
                    case "S":           # Stop playing sound
                        stop_sound()
                    case "A":           # Add new sound
                        new_dict = add_sound()
                        profile.append(new_dict)
                        update_json()
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
    main()
