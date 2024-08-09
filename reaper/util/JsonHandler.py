import json
import os


def init_json():
    if os.path.isfile(noreplylist) == False:
        new_json(noreplylist)
    if os.path.isfile(allowedchannels) == False:
        new_json(allowedchannels)
    if os.path.isfile(neverreplylist) == False:
        new_json(neverreplylist)
    if os.path.isfile(allowedusers) == False:
        new_json(allowedusers)


def new_json(name):
    fp = open(name, "w")
    fp.write("{}")
    fp.close()


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def load_json(file):
    with open(file, "r") as f:
        data = json.load(f)
    return data


# Functions for saving users toggling their replies to JSON
def save_users(data):
    save_json(noreplylist, data)


def load_users():
    return load_json(noreplylist)


# Functions for saving me toggling user abilities to toggle replies to JSON
def save_neverusers(data):
    save_json(neverreplylist, data)


def load_neverusers():
    return load_json(neverreplylist)


# Functions for saving allowed channels to JSON
def save_channels(data):
    save_json(allowedchannels, data)


def load_channels():
    return load_json(allowedchannels)


def save_allowed_users(data):
    save_json(allowedusers, data)


def load_allowed_users():
    return load_json(allowedusers)


config = load_json("config.json")
noreplylist = config["noreplylist"]
neverreplylist = config["neverreplylist"]
allowedchannels = config["allowedchannels"]
allowedusers = config["allowedusers"]
