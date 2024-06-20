import json
import pygame
from pygame import mixer_music as mix
from raspgui import run

run_in_cmd = True
file = "profile.json"

# JSON format is: overall_list = [{"sound": "sounds/...", "text": "Name", "img": "imgs/...", "vol": 100}, {"sound":...}]


def update_json(profile):
    fp = open(file, "w")
    json.dump(profile, fp)
    fp.close()


def add_sound():
    if run_in_cmd:
        sound = input("Input sound path: ")
        name = input("Input sound name: ")
        vol = input("Input sound volume (out of 100): ")
        new_dict = {"sound": sound, "text": name, "volume": vol}

    return new_dict
def main():
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

    while is_running:
        if run_in_cmd:
            cmd = input("Select sound to play (numeric), stop playing sound (S), enter edit mode (E), add sound (A), or quit (Q): ")
            if cmd.isdigit():
                num = int(cmd)
                if num < keys:
                    sel = profile[num]
                    print("Now playing " + sel["text"] + "...")
                    mix.set_volume(int(sel["volume"]) / 100)
                    mix.load(sel["sound"])
                    mix.play()
                else:
                    print("No such sound exists...")
            if cmd == "S":
                mix.stop()
            if cmd == "A":
                new_dict = add_sound()
                profile.append(new_dict)
                keys = len(profile)
                update_json(profile)
            if cmd == "Q":
                is_running = False
                print("See ya!")


if __name__ == "__main__":
    main()
