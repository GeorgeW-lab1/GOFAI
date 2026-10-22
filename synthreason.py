#!/usr/bin/env python3
# Copyright. George Frederick Wagenknecht - 2015/2016/2017
"""
SynthReason - all-in-one
========================
One program that combines the three original C++ programs:

    configurator.cpp -> menu 1  "Configure"            (writes Config.txt)
    learn.cpp        -> menu 2  "Learn / chat"         (SynthReason v0.2g)
                        menu 3  "Teach from text file" (the 'load file' command)
    main.cpp         -> menu 4  "Run 0.9N"             (BiConsciousSymmetricalProcessor)

Typical workflow
    1. Configure  (once; or just accept the defaults)
    2. Put words, one per line, into the lexicon files (names.txt, verbs.txt, ...)
    3. Teach      (reads test.txt and builds knowledgebase.txt)
    4. Run 0.9N   (uses knowledgebase.txt)

Usage
    python synthreason_allinone.py                 # menu
    python synthreason_allinone.py configure
    python synthreason_allinone.py learn
    python synthreason_allinone.py teach [file]    # default test.txt
    python synthreason_allinone.py run [kbfile]    # default knowledgebase.txt
    python synthreason_allinone.py status
    add --allow-shell to let the program run shell commands (see README note below)

NOTE: the original programs could pass text to the operating system shell
(system(...)). That is disabled by default here; start with --allow-shell to
turn it on.
"""

import argparse
import os
import random
import re
import sys

# ----------------------------------------------------------------------------
# Settings / globals
# ----------------------------------------------------------------------------
ALLOW_SHELL = False
MATCH_MODE = "substring"        # "line"      = v0.2g exact-line lexicon match
                                # "substring" = 0.9N substring lexicon match
CONFIG_FILE = "Config.txt"
KNOWLEDGEBASE = "knowledgebase.txt"
LOADFILE_PATH = "test.txt"

# Request descriptors (what the original called desname, desobject, ...)
DES = {
    "action": "how", "bridge": "bridge", "command": "command",
    "concept": "concept", "description": "describe", "emotion": "feel",
    "name": "who", "number": "count", "object": "what", "place": "where",
    "reason": "why", "game": "game", "time": "when",
}
# Word-category files (what the original called desnameF, desobjectF, ...)
LEX = {
    "action": "actions.txt", "bridge": "bridges.txt", "command": "Command.txt",
    "concept": "concept.txt", "description": "descriptions.txt",
    "emotion": "emotion.txt", "name": "names.txt", "number": "Numbers.txt",
    "object": "objects.txt", "place": "places.txt", "reason": "reason.txt",
    "game": "game.txt", "time": "time.txt",
}
# Order in which Config.txt stores them: line 2*i = descriptor, 2*i+1 = filename
CATEGORIES = ["action", "bridge", "command", "concept", "description",
              "emotion", "name", "number", "object", "place", "reason",
              "game", "time"]
# Order the configurator asks them in (same as the original configurator.cpp)
CONFIGURATOR_ORDER = ["name", "object", "action", "time", "description",
                      "number", "reason", "place", "emotion", "command",
                      "bridge", "game", "concept"]
# Fixed extra descriptors / files (not configurable in the originals)
DES_EXTRA = {"adj": "desadj", "adjp": "desadjp", "adv": "desadv",
             "advtime": "desadvtime", "prep": "desprep",
             "qualities": "desqualities", "verb": "desverb"}
FILE_EXTRA = {"adj": "adj.txt", "adjp": "adjpeople.txt", "adv": "adv.txt",
              "advtime": "advtime.txt", "prep": "prep.txt",
              "qualities": "qualities.txt", "verb": "verbs.txt",
              "reply": "reply.txt"}

# engine state
theanswerreadystatic = ""
synthreasonword = ""
synthcom = ""
speedprocessing = 0
found = 0
searchset = 1                   # what to search for (view code for details)
markerc1 = markerc2 = markerc3 = 0
wordpos = 0
wordc = 0
trade = 0
buy = 0.0
sell = 0.0
a = 0
b = 0
m = 0
procnote = 0
synthanswer = ""
anscount = 0
ucount = wordcount = wordcountstat = 0
fail = 0
points = 0
question = 0
lineneeded = ""
textneeded = ""
notes = ""
objects = ""
chainreason = ""
Sout = ""
fileone = "fileone.txt"
filetwo = "filetwo.txt"
thought = [""] * 1024
structure = [""] * 1024
sweep = 0
userinputall = ""
session_kb = ""


class BackToMenu(Exception):
    pass


# ----------------------------------------------------------------------------
# Helpers (emulate C++ std::string / stream behaviour)
# ----------------------------------------------------------------------------
def substr(s, pos, length=None):
    """std::string::substr. A negative length behaves like npos (rest of string)."""
    if pos < 0:
        pos = 0
    if length is None or length < 0:
        return s[pos:]
    return s[pos:pos + length]


def leading_int(s):
    """stringstream(s) >> int"""
    mt = re.match(r"\s*([+-]?\d+)", s)
    return int(mt.group(1)) if mt else 0


_file_cache = {}


def file_data(path):
    """(lines, joined_text) of a file. Cached until the file changes.
    Handles Windows (CRLF) line endings; a missing file reads as empty."""
    try:
        st = os.stat(path)
    except OSError:
        return [], ""
    key = (st.st_mtime_ns, st.st_size)
    hit = _file_cache.get(path)
    if hit and hit[0] == key:
        return hit[1], hit[2]
    with open(path, "r", errors="ignore") as f:
        text = f.read()
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    _file_cache[path] = (key, lines, "".join(lines))
    return lines, "".join(lines)


def read_lines(path):
    return file_data(path)[0]


def run_shell(cmd):
    if ALLOW_SHELL:
        os.system(cmd)
    else:
        print("[shell disabled] would run: " + cmd +
              "   (start with --allow-shell to enable)")


# ----------------------------------------------------------------------------
# Config  +  Configurator (configurator.cpp)
# ----------------------------------------------------------------------------
def Config():
    """Load Config.txt (written by Configurator). Returns True if it existed."""
    if not os.path.isfile(CONFIG_FILE):
        return False
    lines = read_lines(CONFIG_FILE)
    for i, cat in enumerate(CATEGORIES):
        if 2 * i < len(lines) and lines[2 * i].strip():
            DES[cat] = lines[2 * i].strip()
        if 2 * i + 1 < len(lines) and lines[2 * i + 1].strip():
            LEX[cat] = lines[2 * i + 1].strip()
    print("Config file loaded.\n")
    return True


def Configurator():
    print("Configure request descriptors & Word catagories")
    print("(press Enter to keep the value shown in [brackets])\n")
    for n, cat in enumerate(CONFIGURATOR_ORDER, 1):
        d = input("#%d Vocabulary Descriptor [%s]:" % (n, DES[cat])).strip()
        f = input("#%d Filename [%s]:" % (n, LEX[cat])).strip()
        if d:
            DES[cat] = d
        if f:
            LEX[cat] = f

    with open(CONFIG_FILE, "w") as fh:
        fh.write("\n".join(DES[c] + "\n" + LEX[c] for c in CATEGORIES))

    # create the category files (existing files are NOT wiped)
    for cat in CATEGORIES:
        if not os.path.exists(LEX[cat]):
            open(LEX[cat], "w").close()
    ensure_data_files(quiet=True)
    print("Complete!")


# ----------------------------------------------------------------------------
# Data file helpers
# ----------------------------------------------------------------------------
def lexicon_files():
    """All word-category files the engine looks at."""
    files = [LEX[c] for c in CATEGORIES if c != "game"]
    files += [FILE_EXTRA[k] for k in ("adj", "adjp", "adv", "advtime",
                                      "prep", "qualities", "verb", "reply")]
    return files


def ensure_data_files(quiet=False):
    made = []
    for f in lexicon_files():
        if not os.path.exists(f):
            open(f, "w").close()
            made.append(f)
    if made and not quiet:
        print("Created empty word files: " + ", ".join(made))
    return made


def status():
    print("\nData files (words, one per line):")
    empty = 0
    for f in lexicon_files():
        n = sum(1 for l in read_lines(f) if l.strip())
        empty += (n == 0)
        print("  %-18s %s" % (f, "%d words" % n if n else "EMPTY"))
    for f in (LOADFILE_PATH, KNOWLEDGEBASE, "response.txt", "skim.txt",
              "ginsight.txt", "self.txt"):
        print("  %-18s %s" % (f, "%d bytes" % os.path.getsize(f)
                              if os.path.isfile(f) else "(missing)"))
    if empty:
        print("\n%d word files are empty, so nothing can be recognised yet. "
              "Add words (one per line) to them." % empty)
    print()


# ----------------------------------------------------------------------------
# Engine (learn.cpp / main.cpp)
# ----------------------------------------------------------------------------
def loadfile(file):
    global textneeded

    textneeded = ""
    for line in read_lines(file):
        textneeded = textneeded + line

    chars = ",:<>[]"
    for ch in chars:
        textneeded = textneeded.replace(ch, "")

    textneeded = textneeded + " END."
    return textneeded


def filesearch(segment, file):
    lines, joined = file_data(file)
    if MATCH_MODE == "line":                 # v0.2g: whole-line match
        return 1 if segment in lines else 0
    return 1 if joined.find(segment) != -1 else 0   # 0.9N: substring ("speedhack")


def processlogic(answerstringsegment):
    # linear progression: 0 null, 1 right, 2 left, 3 cross transition
    # 3D: 4 null, 5 x+, 6 x-, 8 y+, 9 y-, 10 z+, 11 z-
    # 4D: 12 null, 13 time+, 14 time-
    progression = 0
    foo = ""
    if answerstringsegment.find("are") > 0:
        progression = 1
    if answerstringsegment.find("aren't") > 0:
        progression = 1
    return foo


# MCM (deep learning component) needs processlogic to work!
def processresponselogic():
    global fail
    fail = 0
    return ""


def processresponsealgbraic(answerstring, userinput):
    global ucount, wordcount, wordcountstat, synthanswer, synthreasonword
    global theanswerreadystatic, fail, Sout

    answerstringsegment = ""
    theanswer = ""
    theanswerready = ""
    theanswerreadyreal = ""

    # count words from userinput.
    ucountpos = 0
    userinputcmod = userinput + " "
    while ucountpos < len(userinputcmod) - 2:
        ucount += 1
        ucountpos += 1
        ucountpos = userinputcmod.find(" ", ucountpos)
        if ucountpos == -1:
            break
    ucount -= 1

    # lexicon files, in the original order
    wordcheck_files = [LEX["command"], LEX["bridge"], LEX["concept"],
                       LEX["object"], FILE_EXTRA["reply"], LEX["name"],
                       LEX["reason"], LEX["time"], LEX["place"],
                       LEX["emotion"], LEX["action"], LEX["description"],
                       LEX["number"], FILE_EXTRA["adj"], FILE_EXTRA["adjp"],
                       FILE_EXTRA["adv"], FILE_EXTRA["advtime"],
                       FILE_EXTRA["prep"], FILE_EXTRA["qualities"],
                       FILE_EXTRA["verb"]]

    segmentstart = 0
    segmentend = 0
    while 0 <= segmentend < len(answerstring) - 1:
        answered = 0
        wordcount = 0
        completion = 0
        segmentstart = answerstring.find("[", segmentend)
        segmentend = answerstring.find("]", segmentstart) if segmentstart > -1 else -1
        if segmentstart > -1:
            answerstringsegment = substr(answerstring, segmentstart,
                                         segmentend - segmentstart + 1)
        pos = 0
        posend = 0
        lineend = userinput.find(":", 1)
        while posend != lineend - 1:
            posend = userinput.find(" ", pos + 1)
            word = substr(userinput, pos, posend - pos)
            pos = posend
            if pos == -1:      # guard (C++ would run off the end of the string)
                break
            if word.find(" ") == 0:
                word = word[1:]

            wordcheck2 = 0
            while 0 <= wordcheck2 < len(answerstringsegment) - 2:
                wordcheck2 = answerstringsegment.find(word, wordcheck2 + 1)
                if wordcheck2 == -1:
                    break
                deviseanswerpos = answerstringsegment.find(">", wordcheck2)
                deviseanswerlimit = answerstringsegment.find(":", wordcheck2)
                if deviseanswerpos > -1 and deviseanswerlimit > -1:
                    if deviseanswerlimit > deviseanswerpos:
                        theanswer = answerstringsegment[deviseanswerpos + 1:deviseanswerlimit]
                        if userinput.find(theanswer) == -1:
                            theanswerready = theanswer + " "
            wordcheck = 0

            if trade == 0:
                for f in wordcheck_files:
                    wordcheck += filesearch(word, f)
                # get word des match
                synthanswer = ""
                if userinput.find("?") == -1:
                    if filesearch(word, LEX["place"]) == 1:
                        synthanswer = DES["place"] + " is the " + word + "?"
                        synthreasonword = word
                    if filesearch(word, LEX["object"]) == 1:
                        synthanswer = DES["object"] + " is " + word + "?"
                        synthreasonword = word
                    if filesearch(word, LEX["action"]) == 1:
                        synthanswer = DES["action"] + " does one " + word + "?"
                        synthreasonword = word
                    if filesearch(word, LEX["description"]) == 1:
                        synthanswer = DES["description"] + " a " + word + "?"
                        synthreasonword = word
                    if filesearch(word, LEX["reason"]) == 1:
                        synthanswer = DES["reason"] + " does one " + word + "?"
                        synthreasonword = word
                    if filesearch(word, LEX["name"]) == 1:
                        synthanswer = DES["object"] + " does " + word + " do" + "?"
                        synthreasonword = word

                if wordcheck > 0:
                    wordcountstat += 1
                if question > -1:
                    if wordcheck > 0:
                        wordcount += 1
                        if answerstringsegment.find(word) > -1:
                            completion += 1

        if answered == 0 or answered == 1:
            if completion == wordcount and wordcount > 0:
                theanswerreadyreal += theanswerready + " "
                theanswerreadystatic = theanswerready + " "
                answered = 1
                Sout += "->" + theanswerready
            if completion != wordcount and wordcount > 0:
                fail = 1
                # logic (todo): foo = processlogic(answerstringsegment)

    return theanswerreadyreal


def processlanguage(userinput):
    global markerc1, markerc2, markerc3, anscount, question
    global wordpos, wordc, buy, sell, found, notes

    answerstring = ""
    markerc1 = markerc2 = markerc3 = 0
    pos = 0
    posend = 0
    anscount = 0

    question = userinput.find("?")
    if question == -1:
        lineend = userinput.find(":", 1)
        answerstring = answerstring + "[:"
        while posend != lineend - 1:
            posend = userinput.find(" ", pos + 1)
            word = substr(userinput, pos, posend - pos)
            pos = posend
            if pos == -1:      # guard (C++ would run off the end of the string)
                break
            if word.find(" ") == 0:
                word = word[1:]

            if trade == 1:
                if searchset == 0:
                    for line in read_lines(filetwo):
                        wordpos = 0
                        wordc = 0
                        while wordpos != -1:
                            wordpos = line.find(" ", wordpos + 1)
                        getmatch = line.find(word)
                        if getmatch > -1 and word not in ("a", "in", "or", "by"):
                            markerc1 += 1
                            if markerc1 == wordc:
                                buy += 1

                    for line2 in read_lines(fileone):
                        wordpos = 0
                        wordc = 0
                        while wordpos != -1:
                            wordpos = line2.find(" ", wordpos + 1)
                            wordc += 1
                        getmatch = line2.find(word)
                        if getmatch > -1 and word not in ("a", "in", "or", "by"):
                            markerc2 += 1
                            if markerc2 == wordc:
                                sell += 1

                if searchset == 1:
                    for line3 in read_lines("skim.txt"):
                        wordpos = 0
                        wordc = 0
                        while wordpos != -1:
                            wordpos = line3.find(" ", wordpos + 1)
                            wordc += 1
                        getmatch = line3.find(word)
                        if getmatch > -1 and word not in ("a", "in", "or", "by"):
                            markerc3 += 1
                            if markerc3 == wordc:
                                found += 1
                                notes += userinput + ":"

            if trade == 0:
                # one block per word category, same order as the originals
                lexicons = [
                    (LEX["command"],         DES["command"]),
                    (LEX["concept"],         DES["concept"]),
                    (LEX["bridge"],          DES["bridge"]),
                    (LEX["number"],          DES["number"]),
                    (LEX["name"],            DES["name"]),
                    (LEX["time"],            DES["time"]),
                    (LEX["reason"],          DES["reason"]),
                    (LEX["place"],           DES["place"]),
                    (LEX["emotion"],         DES["emotion"]),
                    (LEX["action"],          DES["action"]),
                    (LEX["description"],     DES["description"]),
                    (LEX["object"],          DES["object"]),
                    (FILE_EXTRA["adj"],      DES_EXTRA["adj"]),
                    (FILE_EXTRA["adjp"],     DES_EXTRA["adjp"]),
                    (FILE_EXTRA["adv"],      DES_EXTRA["adv"]),
                    (FILE_EXTRA["advtime"],  DES_EXTRA["advtime"]),
                    (FILE_EXTRA["prep"],     DES_EXTRA["prep"]),
                    (FILE_EXTRA["qualities"], DES_EXTRA["qualities"]),
                    (FILE_EXTRA["verb"],     DES_EXTRA["verb"]),
                ]
                for lexfile, requestdescriptors in lexicons:
                    if filesearch(word, lexfile) == 1:
                        answerstring = answerstring + requestdescriptors + ">" + word + ":"
                        anscount += 1
        answerstring += "]"
    return answerstring


# NOTE: SYNTAXEXTRACTOR, GETPREPOSITION, DATAACTIVATOR, RESPONSEINITPROCESSOR
# and SYNTAXBRANCHER are commented out in the original sources and omitted.


def processKnowledge(userinput, knowledgebase, interactive=False):
    """One pass of the original processKnowledge (0.9N) / main loop (v0.2g).
    interactive=True adds the v0.2g behaviour: USER: prompt, NLP.txt output,
    echo, optional shell command and the [answer] print."""
    global ucount, wordcountstat, speedprocessing, trade, a, b, m, procnote
    global notes, textneeded, lineneeded, chainreason, objects, synthcom
    global question, sweep, userinputall, session_kb

    theanswerready = ""
    sentstruc = 0
    line = ""
    ucount = 0
    wordcountstat = 0
    if interactive:
        print()

    answerstring = session_kb
    if os.path.isfile(knowledgebase):
        with open(knowledgebase, "rb") as fh:
            answerstring = fh.read().decode("latin-1")

    if sweep == 0:
        speedprocessing = 0
        if interactive:
            userinput = input("USER: ")
            if userinput.strip().lower() in ("quit", "exit", "menu"):
                raise BackToMenu()

    if userinput == "load file":
        userinputall = loadfile(LOADFILE_PATH)
        speedprocessing = 1
        userinput = ""
        sweep = 1

    if userinput == "open new window":
        run_shell("start main.exe")

    if userinput == "show answerstring":
        userinput = ""
        print(answerstring, end="")

    if userinput == "show thought":
        userinput = ""
        print(thought[0], end="")
    if userinput == "show structure":
        userinput = ""
        print(structure[0], end="")

    if speedprocessing == 1:
        answerstring = ""

    if userinput == "load insight":
        userinput = ""
        for linei in read_lines("ginsight.txt"):
            userinput = "you want " + linei + " :"
            answerstring += processlanguage(userinput)
        for linei in read_lines("self.txt"):
            userinput = "you are " + linei + " :"
            answerstring += processlanguage(userinput)

    if userinput == "switch mode":
        userinput = ""
        # (as in the original, the two ifs cancel each other out)
        if trade == 0:
            trade = 1
        if trade == 1:
            trade = 0

    if userinput == "E41A":
        userinput = ""
        while 0 == 0:           # original behaviour: endless ERROR (Ctrl+C to stop)
            print("ERROR")

    if userinput == "E41B":
        userinput = ""
        userinputall = ""
        answerstring = ""
        textneeded = ""
        lineneeded = ""
        notes = ""
        line = ""

    if userinput == "trade?":
        userinput = ""
        temp1 = 0.0
        combine = int(buy + sell)
        divbuy = buy / combine if combine else 0.0
        divsell = sell / combine if combine else 0.0
        divbuy *= 100
        divsell *= 100
        if divbuy > 50:
            print("ACTION: BUY, ", end="")
            temp1 = divbuy - 50
        if divsell > 50:
            print("ACTION: SELL, ", end="")
            temp1 = divsell - 50
        if divbuy == 50:
            print("ACTION: NOTHING, ", end="")
            temp1 = divbuy - 50

        print("Probability of Success: ", end="")
        if temp1 >= 0 and temp1 < 2:
            print("CRITICALLY LOW")
        if temp1 <= 3 and temp1 > 2:
            print("LOW")
        if temp1 <= 4 and temp1 > 3:
            print("MEDIUM")
        if temp1 <= 5 and temp1 > 4:
            print("HIGH")
        if temp1 <= 6 and temp1 > 5:
            print("VERY HIGH")
        if temp1 > 6:
            print("Guaranteed ")

        print("Points: ", temp1)
        print("Buy markers: ", buy, " Sell markers: ", sell)

    if userinput == "found?":
        userinput = ""
        print("number found: ", found)

    if userinput == "show notes":
        userinput = ""
        print(notes, end="")
        m += 1

    if userinput == "process info":
        run_shell('start main "web.txt"')

    if userinput == "show userinputall":
        userinput = ""
        print(userinputall, end="")
        m += 1

    if userinput == "show reasonchain":
        print(chainreason, end="")

    if userinput == "think":
        structposA = 0
        thoughtposA = 0
        structurestr = structure[0]
        thoughtstr = thought[0]
        o = 0
        while o < 10:
            structposB = structurestr.find(" ", structposA)
            print("STRUCT:", structposA, structposB, end="")
            structposA = structposB + 1
            thoughtposB = thoughtstr.find(" ", thoughtposA)
            print("  PROCESS:", thoughtposA, thoughtposB)
            thoughtposA = thoughtposB + 1
            o += 1

    if userinput == "open auto window":
        run_shell('main "auto.txt"')

    if userinput == "save notes":
        userinput = ""
        with open("notes.txt", "w") as textfile0:
            textfile0.write(notes)

    if userinput == "process notes":
        userinput = ""
        trade = 0
        sweep = 1
        procnote = 1

    if sweep == 1:
        if procnote == 1:
            userinputall = notes + ":"

        if procnote == 0:
            b = userinputall.find(".", a + 2)
            userinput = substr(userinputall, a, b - a + 1)
            a = userinputall.find(".", a + 1)

        if procnote == 1:
            b = userinputall.find(":", a + 2)
            userinput = substr(userinputall, a, b - a + 1)
            a = userinputall.find(":", a + 1)

    if a == len(userinputall) - 1:
        sweep = 0
        a = 0
        b = 0

    if procnote == 0:
        remdot = userinput.find(".")
        if remdot == 0:
            userinput = userinput[1:]
        remdot = userinput.find(".")
        if remdot > 0:
            userinput = userinput[:-1]
    if procnote == 1:
        remdot = userinput.find(":")
        if remdot == 0:
            userinput = userinput[1:]
        remdot = userinput.find(":")
        if remdot > 0:
            userinput = userinput[:-1]

    question = userinput.find("?")
    if question > -1:
        userinput = userinput[:question]
        userinput += " ?"
    if procnote == 0:
        userinput = userinput + " :"

    if sentstruc == 0:
        answerstring += processlanguage(userinput)
    if trade == 0:
        if sentstruc == 0:
            theanswerready = processresponsealgbraic(answerstring, userinput)

    numresp = leading_int(theanswerready)
    chainreason += theanswerready
    if userinput.find("why") > -1:
        chainreason += "~"
    elif userinput.find("what") > -1:
        chainreason += "^"
    elif userinput.find("when") > -1:
        chainreason += "&"
    elif userinput.find("how") > -1:
        chainreason += "*"
    elif userinput.find("describe") > -1:
        chainreason += "+"
    elif userinput.find("who") > -1:
        chainreason += "#"

    if numresp < 200 and numresp > 0:
        x = 1
        for respline in read_lines("response.txt"):
            if x == numresp:
                print(respline)
            x += 1

    if speedprocessing == 1:
        with open(knowledgebase, "a") as textfile4:
            textfile4.write(answerstring)

    if interactive:
        with open("NLP.txt", "w") as NLP:
            NLP.write(theanswerready)
        print(userinput, end="")

    if userinput.find(DES["command"]) != -1:
        for line in read_lines(LEX["object"]):
            pos = userinput.find(line)
            if pos != -1:
                objects = line
        synthcom = theanswerready + " " + objects
        print("\n" + synthcom)
        if interactive:
            run_shell(synthcom)      # original: system(synthcom)

    if interactive:
        print("[" + theanswerready + "]", end="")

    session_kb = answerstring
    return theanswerready


# ----------------------------------------------------------------------------
# Modes
# ----------------------------------------------------------------------------
def learn_mode(kb=KNOWLEDGEBASE):
    """learn.cpp  -  SynthReason v0.2g interactive loop."""
    global MATCH_MODE
    MATCH_MODE = "line"
    print("the developer is not responsible for the user's intent using this program.")
    print("SynthReason.  v0.8a   (type 'menu' to go back)")
    print("Commands: load file, show answerstring, show notes, trade?, found?, "
          "process notes, save notes, ...")
    try:
        while True:
            processKnowledge("", kb, interactive=True)
    except (BackToMenu, EOFError, KeyboardInterrupt):
        print()


def teach(path=None, kb=KNOWLEDGEBASE):
    """The 'load file' command as a one-shot: read a text file sentence by
    sentence and append the tagged result to the knowledge base."""
    global MATCH_MODE, LOADFILE_PATH, sweep, speedprocessing
    path = path or LOADFILE_PATH
    if not os.path.isfile(path):
        print("Cannot find '%s'. Put some plain text in it (sentences ending "
              "in '.') and try again." % path)
        return
    if not any(l.strip() for f in lexicon_files() for l in read_lines(f)):
        print("Warning: all word files are empty, so nothing will be tagged. "
              "Fill names.txt, verbs.txt, etc. first (see 'status').")
    MATCH_MODE = "line"
    LOADFILE_PATH = path
    before = os.path.getsize(kb) if os.path.isfile(kb) else 0
    sweep = 0
    sentences = 1
    processKnowledge("load file", kb)
    while sweep == 1:
        processKnowledge("", kb)
        sentences += 1
    speedprocessing = 0
    after = os.path.getsize(kb) if os.path.isfile(kb) else 0
    print("Learned from %d sentence(s); %s grew by %d bytes."
          % (sentences, kb, after - before))


def run_mode(kb=None):
    """main.cpp  -  SynthReason 0.9N (BiConsciousSymmetricalProcessor)."""
    global MATCH_MODE, Sout

    MATCH_MODE = "substring"
    ent = 7
    print("SynthReason 0.9N (BiConsciousSymmetricalProcessor)- Beta - "
          "George Wagenknecht - Jan 2017")
    try:
        processTool = kb or (input("\nInitilise KnowledgeBase [%s]:" % KNOWLEDGEBASE).strip()
                             or KNOWLEDGEBASE)
        if not os.path.isfile(processTool) or os.path.getsize(processTool) == 0:
            print("Note: '%s' is missing or empty - 0.9N has nothing to think "
                  "with. Use 'Teach' first." % processTool)
        word1 = ""
        # ($universe/system) control logic / ethics / mandates strings of the
        # original are only referenced from commented-out code.

        while 0 == 0:
            with open("logout.txt", "a") as logout:
                logout.write("Initiating Lexeme Processor:\n")
            processToolprev = processTool
            with open("status.txt", "w"):
                pass
            CC = ""
            # description / verb / qualities cycle (original structarray)
            structarray = [DES_EXTRA["verb"], DES["description"], DES_EXTRA["qualities"]]
            J = 0
            Core = ",conscious,"
            s1 = 0
            s2 = 0
            loop = 0

            key = input("\nContext (blank or 'menu' = back):").strip()
            if key.lower() in ("", "menu", "quit", "exit"):
                return

            while 0 == 0:
                if processTool == "thought":
                    aa = "".join(read_lines("RDB2"))
                    with open("memory", "a") as qq:
                        qq.write(aa)
                    with open("RDB2", "w"):
                        pass

                # CORE PROTECTION
                s1 = Core.find(",", s1)
                s2 = Core.find(",", s1 + 1)

                with open("logout.txt", "a") as logout:
                    logout.write(processToolprev + " ==> " + processTool + "\n")

                xoxo = structarray[J]
                J += 1
                if J == 2:
                    J = 0

                Logicthinkdescribe = xoxo + " " + key + "?"

                with open("logout.txt", "a") as logout:
                    logout.write(Logicthinkdescribe + " " + processTool + "\n")

                processKnowledge(Logicthinkdescribe, processTool)
                start = 0
                num = random.randint(1, ent)
                line = Sout
                while num != ent // 2:
                    num = random.randint(1, ent)
                    test = line.find(">", start + 1)
                    test1 = line.find(">", test + 1)
                    if test1 == -1:
                        start = 0

                    length1 = line.find(">", start + 1)
                    length2 = line.find(" ", length1 + 1)

                    word1 = substr(line, length1 + 1, length2 - length1 - 1)
                    start = length2
                    if start < 0:       # keep find() positions sane (C++ npos wrap)
                        start = 0

                key = word1
                print((word1 if word1 else "(nothing learned yet)") + " ", end="", flush=True)

                if processTool == "conscious":
                    CC = ""

                if loop == 6:
                    break
                loop += 1
    except (EOFError, KeyboardInterrupt):
        print()


# ----------------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------------
def menu():
    while True:
        print("""
SynthReason - all in one
  1  Configure descriptors & word files   (configurator)
  2  Learn / chat                         (v0.2g)
  3  Teach from a text file               (builds knowledgebase.txt)
  4  Run SynthReason 0.9N
  5  Status / check data files
  0  Quit""")
        try:
            choice = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if choice == "1":
            Configurator()
        elif choice == "2":
            learn_mode()
        elif choice == "3":
            try:
                p = input("Text file to learn from [%s]:" % LOADFILE_PATH).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                continue
            teach(p or None)
        elif choice == "4":
            run_mode()
        elif choice == "5":
            status()
        elif choice in ("0", "q", "quit", "exit"):
            return


def main(argv=None):
    global ALLOW_SHELL, LOADFILE_PATH, KNOWLEDGEBASE
    ap = argparse.ArgumentParser(description="SynthReason all-in-one")
    ap.add_argument("command", nargs="?",
                    choices=["configure", "learn", "teach", "run", "status"])
    ap.add_argument("file", nargs="?", help="text file (teach) or knowledge base (run)")
    ap.add_argument("--allow-shell", action="store_true",
                    help="allow commands to be run through the OS shell")
    args = ap.parse_args(argv)
    ALLOW_SHELL = args.allow_shell

    if not Config():
        print("No %s yet - using default descriptors (choose 1 to configure)." % CONFIG_FILE)
    ensure_data_files()

    if args.command == "configure":
        Configurator()
    elif args.command == "learn":
        learn_mode()
    elif args.command == "teach":
        teach(args.file)
    elif args.command == "run":
        run_mode(args.file)
    elif args.command == "status":
        status()
    else:
        menu()
    return 0


if __name__ == "__main__":
    sys.exit(main())
