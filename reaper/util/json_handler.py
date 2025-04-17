import json
import os

from util import global_variables


def init_json():
    if not os.path.isfile(noreplylist):
        new_json(noreplylist)
    if not os.path.isfile(allowedchannels):
        new_json(allowedchannels)
    if not os.path.isfile(neverreplylist):
        new_json(neverreplylist)
    if not os.path.isfile(allowedusers):
        new_json(allowedusers)


def new_json(name):
    with open(name, "w") as f:
        json.dump({}, f)


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


def load_allowed_channels():
    return load_json(allowedchannels)


def save_allowed_users(data):
    save_json(allowedusers, data)


def load_allowed_users():
    return load_json(allowedusers)


noreplylist = global_variables.config["general"]["noreplylist"]
neverreplylist = global_variables.config["general"]["neverreplylist"]
allowedchannels = global_variables.config["general"]["allowedchannels"]
allowedusers = global_variables.config["general"]["allowedusers"]
