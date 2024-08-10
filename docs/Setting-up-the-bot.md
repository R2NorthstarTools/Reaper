## Dependencies

Spectre uses the following dependencies for "normal" use:\
`discord.py`\
`python-dotenv`

Spectre uses the following dependencies for the update file:\
`gitpython` 

Spectre uses the following dependencies for the `price` command:\
`bs4`\
`lxml` 

Spectre uses the following dependencies for the "image reading" functionality:\
`pytesseract`\
[Tesseract binaries](https://tesseract-ocr.github.io/tessdoc/)

If you don't want to set one of the non required ones up, you can simply not install them and remove/comment out the relevant files (making sure to remove them in the main `Spectre.py` file to not encounter issues).

You can install these at a "controlled" version with Poetry by first installing poetry (`curl -sSL https://install.python-poetry.org | python3 -` in a terminal), using `cd` to get into the `Spectre` directory, then running `poetry install`\
Or you can install them by using `pip install discord.py python-dotenv gitpython bs4 lxml` in a terminal.

If your pr adds a dependency, please add it to the poetry list by using `cd` to get into the `Spectre` directory, then run `poetry add DEPENDENCY_NAME_HERE`.

## `.env` file

Spectre relies on using a file called `.env` with the library `python-dotenv` to load sensitive information.\
It requires at the very least having a [Discord bot token](https://discordpy.readthedocs.io/en/stable/discord.html), with an option for a [GitHub access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) for using the GitHub api (only used for fetching Northstar version as of writing) 

It should look like:
```
TOKEN = "PLACEYOURDISCORDBOTTOKENHERE"
GH_ACCESS_TOKEN = "PLACEYOURGITHUBTOKENHERE"
```
Again noting you don't _need_ the GitHub token, and making sure to keep the quotes when pasting in the tokens

## Config file

Inside `config.json` in the bots files, you should see something like this:
```
{
    "admin": 502519988423229460,
    "prefix": "$",
    "cooldowntime": 5, 
    "noreplylist": "data/noreplyusers.json",
    "neverreplylist": "data/neverreplyusers.json",
    "allowedchannels": "data/allowedchannels.json",
    "allowedusers": "data/allowedusers.json"
}
```
These have been edited to be very simple thanks to H0L0 in order to make changing them easy as well. 

To put it simply:\
"admin" refers to the user id of the person you want to be able to use the "big" commands\
"prefix" is the text based fall back prefix instead of the slash command\
"cooldowntime" is how long of a cooldown the bot should have in between automatically replying (in seconds) 

`noreplylist` to `allowedusers` are all paths to store `.json` files containing data that you use when using the bot (such as [allowed channels](https://github.com/itscynxx/Spectre/blob/main/cogs/AllowedChannels.py#L11) and [allowed users](https://github.com/itscynxx/Spectre/blob/main/Spectre.py#L116))

## Updating the bot/testing a branch

Spectre comes with a file called `updateSpectre.py`. This file allows you to run `python3 updateSpectre.py`, then choose if you want to 
1. Update Spectre (clone newest repo, move data files to it)
2. Test a Spectre branch (mainly for me, but you can just input a Spectre branch url for testing and data files move to it automatically)
3. Restore Spectre data (to be used in a Spectre branch from the `test` command, moves data from the current branch folder to the original Spectre folder)

Running the file also runs you through these steps
