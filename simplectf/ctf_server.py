#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
################################################################################
#
#    Copyright 2017 Félix Brezo and Yaiza Rubio (i3visio, contacto@i3visio.com)
#
#
#    This program is part of Terminal-CTF. You can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

__author__ = "Felix Brezo y Yaiza Rubio "
__copyright__ = "Copyright 2015-2017, i3visio"
__credits__ = ["Felix Brezo", "Yaiza Rubio"]
__license__ = "AGPLv3+"
__version__ = "v0.1"
__maintainer__ = "Felix Brezo, Yaiza Rubio"
__email__ = "contacto@i3visio.com"


import argparse
import datetime as dt
import json
import os
import urllib
#import shlex
#import sys

# Server code
import flask
from flask import Flask
from flask import abort, redirect, url_for
from flask import request
from flask import render_template
from flask import send_file


# Starting the app
app = Flask("SimpleCTF")
# The configuration of the challenge
config = {}
dataFolder = "./data"


def underlineText(text, underline="-"):
    """
    A method that underlines a given text.

    Args:
    -----
        text: A string representing the text to be underlined.
        underline: A string representing the character to be used to underline.

    Returns:
    --------
        string: A string containing the original text and a line behind it.
    """
    out = text + "\n"
    for i in range(len(text)):
        out += underline
    return out


def createResponse(text, status=200, content_type="text/plain; charset=utf-8"):
    """
    Simple method that creates the Flask Response.

    Args:
    -----
        text: The text to return.
        status: The status to return. By default, 200.
        content_type: The content_type. By default, `text/plain; charset=utf-8`,
            but it can be `application/json` or others.

    Returns:
    --------
        flask.Response: The Flask Response object that will be returned.
    """
    return flask.Response(text, status=status, content_type=content_type)


def getOrderedResults():
    """
    Returns an ordered list of elements according to their current score.

    Code is obtained from the following Stackoverflow question:
    https://stackoverflow.com/questions/613183/sort-a-python-dictionary-by-value

    It will iterate over a dictionary where the key is the username and it
    contains another dict with two different keys: `points` and
    `solved_challenges`.

    Returns:
    --------
        list: It contains a list of ordered tuples (<username>, <points>) with
            the rank.
    """
    rank = []

    # Getting the status
    resultsPath = os.path.join(dataFolder, config["title"] + "_status.json")

    if not os.path.isfile(resultsPath):
        return rank
    else:
        # Reading the file
        results = json.loads(open(resultsPath, "r").read())

    # Auxiliar structure to simplify the results info
    tmp = {}
    for u in results:
        tmp[u] = results[u]["points"]

    # Ordering the list
    for w in sorted(tmp, key=tmp.get, reverse=True):
        rank.append((w, tmp[w]))
    return rank


@app.route("/")
def getHome():
    text = underlineText(config["title"], underline="=") + "\n\n" + config["description"] + """

Instructions
------------

As a user, the only things you need to know are the following:
- Go to /license to show the license of the application.
- Go to /list to show the available challenges.
- Go to /rank to show the current leaderboard.
- Go to /c/<challenge-title> to show the instructions of that challenge.
- Go to /c/<challenge-title>/<username>/<answer> to send an answer as username.
- Go to /u/<username> to show the challenges solved by the user.

That's all!

License and Disclaimer
----------------------

This (dummy?) CTF is powered by a simple curl-compliant CTF licensed as AGPLv3.
Its source code and installation instructions can be found in the Github
project: https://github.com/i3visio/simple-ctf

Because you don't need a web browser to hack like a *pro*! Enjoy! :)""" + "\n"
    return createResponse(text)


@app.route("/license")
def getLicense():
    text = urllib.urlopen("https://www.gnu.org/licenses/agpl-3.0.txt").read()
    return createResponse(text)


@app.route("/info")
def getInfo():
    info = {
        "__version__": "SimpleCTF " + __version__,
        "license": "AGPLv3",
        "server_time": str(dt.datetime.now()),
        "source_code": "https://github.com/i3visio/simplectf",
    }
    return createResponse(
        json.dumps(
            info,
            indent=2,
            sort_keys=True,
        ) + "\n",
        content_type="application/json"
    )


@app.route("/list")
def getList():
    text = """List of Challenges
==================

"""
    for c in config["challenges"]:
        text += "\t- /c/" + c["url"] + " --> [" + c["type"] + "] " + c["title"] + " (" + str(c["points"]) + " points)\n"
    return createResponse(text)


@app.route("/rank")
def getRank():
    text = """Current Leaderboard
===================

"""
    rank = getOrderedResults()
    if len(rank) == 0:
        text += "No users completed a challenge yet!"
    else:
        for i, r in enumerate(rank):
            try:
                if r[1] == rank[i-1][1] and i != 0:
                    # The number of points is the same so the position is the same
                    pos = " "
                else:
                    pos = str(i+1) + ") "
            except:
                pos = str(i+1) + ") "
            text +=  pos + "\t" + r[0] + " (" + str(r[1]) + " points)\n"
    return createResponse(text)


@app.route("/u/<username>")
def getUser(username=None):
    resultsPath = os.path.join(dataFolder, config["title"] + "_status.json")
    if not os.path.isfile(resultsPath):
        return createResponse("Bad Request: No usernames in the database yet!", status=400)
    else:
        if not username:
            return createResponse("Bad Request: No username was specified!", status=400)
        else:
            results = json.loads(open(resultsPath, "r").read())

            user = results[username]

            text = underlineText("@" + username, underline="=") + "\n\n"
            text += "- Points awarded: " + str(user["points"]) + "\n\n"
            text += "- Challenges solved:\n"
            for c in user["solved_challenges"].keys():
                text += "\t" + c + "\n"

            # Collect the data from the user
            return createResponse(text)

@app.route("/c/<challenge>")
@app.route("/c/<challenge>/<username>")
@app.route("/c/<challenge>/<username>/<answer>")
def getChallenge(challenge, username=None, answer=None):
    # Iterating to grab the challenge
    c = None
    resultsPath = os.path.join(dataFolder, config["title"] + "_status.json")
    # Reading the file
    results = json.loads(open(resultsPath, "r").read())


    for chall in config["challenges"]:
        if challenge == chall["url"]:
            c = chall
            break
    if c:
        text = underlineText(c["title"], underline="=") + "\n\n"

        if not username:
            # Showing the description
            text += c["description"]
            text += "\n\n" + underlineText("How to Push an Answer")
            text += "\nRemember that you can push the solution using the following URL:\n\t/c/" + challenge + "/<username>/<answer>"
            text += "\n\n" + underlineText("Solved by:") + "\n"
            for u in results.keys():
                if challenge in results[u]["solved_challenges"].keys():
                    text += "\t- " + u + "\n"
        elif not answer:
            # No solution provided
            return createResponse("Bad Request: You have provided no solution!", status=400)
        else:
            # Check if the solution is correct or not!
            if answer == c["answer"]:
                text = "Correct answer, " + username + "!\n\n"

                if not os.path.isfile(resultsPath):
                    results = {}
                    results[username] = {
                        "points": c["points"],
                        "solved_challenges": {
                            challenge: c["points"]
                        }
                    }
                    text += "You have solved your first challenge!\nYou have been awarded with " + str(c["points"]) + " for solving it.\n\n"
                else:
                    # Create the username results if it does not exist
                    if username not in results.keys():
                        results[username] = {
                            "points": c["points"],
                            "solved_challenges": {
                                challenge: c["points"]
                            }
                        }
                        text += "You have solved your first challenge!\nYou have been awarded with " + str(c["points"]) + " for solving it.\n\n"
                    elif challenge not in results[username]["solved_challenges"].keys():
                        results[username]["solved_challenges"][challenge] = c["points"]
                        results[username]["points"] += c["points"]
                        text += "You have been awarded with " + str(c["points"]) + " for solving this challenge.\n\n"
                    else:
                        text += "But you have already resolved the challenge before! No more points awarded.\n"
                # Updating the results
                with open(resultsPath, "w") as oF:
                    oF.write(json.dumps(results, indent=2))

                text += username + ", your current point balance is " + str(results[username]["points"]) + " points.\n\n"
                text += "You can always check the full leaderboard in /rank"
            else:
                text = "Incorrect answer, " + username + "! Try again in the following URL:\n\t/c/" + challenge + "/" + username + "/<new_answer>"
    # The challenge provided was not found. Probably a bad request.
    else:
        text = "No challenge found with this title: " + challenge + ". Try /list to found the existing challenges."

    return createResponse(text)


@app.errorhandler(400)
def page_not_found(error):
    text = """
Error 400
=========

Bad Request. Are you sure you made a correct request?

Go back to / to get further instructions.
    """
    return createResponse(text, status=400)


@app.errorhandler(404)
def page_not_found(error):
    text = """
Error 404
=========

Page Not Found. Is this the website you want to visit?

Go back to / to get further instructions.
"""
    return createResponse(text, status=404)


@app.errorhandler(500)
def page_not_found(error):
    text = """
Error 500
=========

Internal Server Error. This should not be happening. Contact the admin if the
error persists.
"""
    return createResponse(text, status=500)


if __name__ == "__main__":
    # Loading the server parser
    parser = argparse.ArgumentParser(
        description='SimpleCTF - A dummy curl-compliant CTF platform developed by i3visio.',
        prog='./ctf_server.py',
        epilog="Check the README.md file for further details on the usage of this program or follow us on Twitter in <http://twitter.com/i3visio>.",
        add_help=False
    )

    # adding the option
    groupServerConfiguration = parser.add_argument_group('Configuration arguments', 'Configuring the processing parameters.')
    groupServerConfiguration.add_argument('--data', required=False, default="./data", action='store', help='choose the data folder where the results will be stored.')
    groupServerConfiguration.add_argument('--debug', required=False, default=False, action='store_true', help='choose whether error messages will be deployed. Do NOT use this for production.')
    groupServerConfiguration.add_argument('--host', metavar='<IP>', required=False, default="localhost", action='store', help='choose the host in which the server will be accesible. If "0.0.0.0" is choosen, the server will be accesible by any remote machine. Use this carefully. Default: localhost.')
    groupServerConfiguration.add_argument('--port', metavar='<PORT>', required=False, default=5000, type=int, action='store', help='choose the port in which the server will be accesible. Use this carefully.')
    groupServerConfiguration.add_argument('--rules', required=True, action='store', help='choose the Json configuration file that defines the CTF.')

    groupAbout = parser.add_argument_group('About arguments', 'Showing additional information about this program.')
    groupAbout.add_argument('-h', '--help', action='help', help='shows this help and exists.')
    groupAbout.add_argument('--version', action='version', version='%(prog)s ' + " " + __version__, help='shows the version of the program and exists.')

    # Parse args
    args = parser.parse_args()
    # Loading configuration
    print("[*] Loading configuration file from " + args.rules + "...")
    config = json.loads(open(args.rules, "r").read())
    print("[*] Setting data folder as " + args.data + "...")
    dataFolder = args.data

    # Starting the server
    print("[*] Server started at " + "http://" + args.host + ":" + str(args.port) + "... You can access it in your browser.")
    print("[*] Press <Ctrl + C> at any time to stop the server.")

    app.run(
        debug=args.debug,
        host=args.host,
        port=args.port
    )

    print("\n[*] Simple CTF closed successfully.")
