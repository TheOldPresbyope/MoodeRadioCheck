#!/usr/bin/python3
""" check mpd can play
    -  single url, or
    -  url in single pls file, or
    -  urls contained line-by-line in a text file, or
    -  url in every pls file in a dir or below, or
    -  url in every pls file in moOde RADIO directory or below
"""

import argparse
import glob
import os
import subprocess
import sys
import time

BITBUCKET = subprocess.DEVNULL


def parse_pls(file):
    """ return the #1 station name and url in pls file
        parses Title1= and File1= entries by brute force
        does no meaningful syntax or semantics checking
        does not check if file has Windows- vs Linux-style line endings
    """
    name = None
    url = None

    with open(file, "r") as fh:
        for line in fh:
            line = line.strip(" \n")
            # there should't be any blank lines, but sometimes...
            if line == "":
                continue
            # this header had to be in first line for file command to
            # identify the file as a pls, so just skip
            if line == "[playlist]":
                continue
            # at least one moOde url has an embedded "=",
            # so split on first one only
            subj, pred = line.split("=", 1)
            subj = subj.strip()
            pred = pred.strip()
            if subj == "File1":
                url = pred
            if subj == "Title1":
                name = pred
            if name and url:
                break
    fh.close()
    return url, name


def try_url(url):
    """ use mpc to submit the url to mpd.
         - crashes out if mpd isn't running
         - returns 0 if mpd can play the url
         - returns 1 and mpd's error message if it can't
         - side effect: leaves MPD queue cleared and volume=0
    """

    # check mpd is running
    res = subprocess.run(["pgrep", "-u", "mpd"],
                         stdout=BITBUCKET, stderr=BITBUCKET)
    if res.returncode == 1:
        sys.exit("oops - mpd process not found")
    # try to be kind to user's ears
    subprocess.run(["/var/www/vol.sh", "0"],
                   stdout=BITBUCKET, stderr=BITBUCKET)
    subprocess.run(["mpc", "clear"], stdout=BITBUCKET, stderr=BITBUCKET)
    # need to check if mpc add returns error msg
    subprocess.run(["mpc", "add", url], stdout=BITBUCKET, stderr=BITBUCKET)
    subprocess.run(["mpc", "play"], stdout=BITBUCKET, stderr=BITBUCKET)
    # this pause may not be necessary but just in case...
    time.sleep(0.5)
    output = subprocess.run(["mpc", "status"], capture_output=True)
    subprocess.run(["mpc", "clear"], stdout=BITBUCKET, stderr=BITBUCKET)
    result = str(output.stdout, "utf-8")
    if "ERROR: " in result:
        return 1, result.partition("ERROR: ")[2].strip("\n")
    else:
        return 0, ""


def check_dir(dir):
    """
    """
    plscount = 0
    goodplscount = 0
    badplscount = 0
    for plsfile in glob.iglob(dir + "/**/*.pls", recursive=True):
        plscount += 1
        radiourl, radioname = parse_pls(plsfile)
        if not radiourl or not radioname:
            badplscount += 1
            print(
                f"{plsfile} missing 'File1=' and/or 'Title1=' line; skip to next pls file\n")
            continue
        result = try_url(radiourl)
        if result[0]:
            badplscount += 1
            print(f"station: {radioname}\nfile: {plsfile}\nMPD {result[1]}\n")
        else:
            goodplscount += 1
            continue
    sys.exit(
        f"{dir} contains {plscount} pls files: {goodplscount} playable and {badplscount} not playable")


def check_url(url):
    """ check if mpd can play the given url, print result, and exit
    """
    result = try_url(url)
    if result[0]:
        sys.exit(f"mpd: {result[1]}\n")
    else:
        sys.exit(f"{url} is a playable url")


def check_file(file):
    """ determine if the given file is a pls file or a text file
        - if pls, check its url
        - if text file, try to find and check urls in it
        - print result and exit
    """
    output = subprocess.run(["file", file], capture_output=True)
    res = str(output.stdout, "utf-8")
    if "ASCII" not in res:
        sys.exit(f"{file} not ASCII text")
    if "PLS" in res:
        radiourl, radioname = parse_pls(file)
        if not radiourl or not radioname:
            sys.exit(f"oops - {file} is missing File1= and/or Title1= line")
        if not radiourl.lower().startswith("http://"):
            sys.exit(f"{file} does not describe an HTTP streaming source")
        result = try_url(radiourl)
        if result[0]:
            sys.exit(f"mpd: {result[1]}\n")
        else:
            sys.exit(f"{file} is a playable pls file")
    else:
        urlcount = 0
        goodcount = 0
        badcount = 0
        with open(file, "r") as fh:
            for line in fh:
                line = line.strip(" \n")
                if line.lower().startswith("http://"):
                    urlcount += 1
                    result = try_url(line)
                    if result[0]:
                        badcount += 1
                        print(f"mpd: {result[1]}\n")
                    else:
                        goodcount += 1
            fh.close()
            if urlcount == 0:
                sys.exit(f"{file} contains no usable url line")
            else:
                sys.exit(
                    f"{file} contains {goodcount} playable urls and {badcount} bad urls")


# Main

parser = argparse.ArgumentParser(
    usage="%(prog)s url|file|dir|RADIO|-h",
    description="check mpd can play a given url, or the url in a given pls file, or the urls contained line-by-line in a given file, or the url in every pls file in a given dir and below, or ('RADIO') the url in every pls file in the moOde RADIO directory and below",
    epilog="NOTES: 1) protect spaces in filename, 2) mpd process must be running")
parser.add_argument("arg", type=str, help="url|file|dir|RADIO")

arg = parser.parse_args().arg
if os.path.isdir(arg):
    check_dir(arg)
elif os.path.isfile(arg):
    check_file(arg)
elif arg == "RADIO":
    check_dir("/var/lib/mpd/music/RADIO")
elif arg.lower().startswith("http"):
    check_url(arg)
else:
    sys.exit(f"oops- what is {arg}?")
