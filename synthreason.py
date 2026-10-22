#!/usr/bin/env python3
# Copyright. George Frederick Wagenknecht - 2016
"""
Artificial Logic Linking System
Note this program is based upon cognitive system I had designed to deal with
the brain injury I suffered, (my own design :) ).
DEV NOTE: REDESIGN STRING LABELS FOR APPROPRIATENESS

Python port of the original C++ source (structure preserved).
"""

import os
import re
import sys
import random
# import hashlib   # replaces sha512.h (only used in the commented-out serial check)

# ----------------------------------------------------------------------------
# Globals
# ----------------------------------------------------------------------------
CHOICE = False
D = E = F = ""
logout = None
# EE / NE: sha512 integrity hashes in the original. They were only referenced
# from commented-out code, so they are left empty here.
EE = ""
NE = ""
filename = ""
k = 0
wordPrev = ""
Sout = ""
space = 0
NCount = 0
Argc = 0
Argv = ""
theanswerreadystatic = ""
synthreasonword = ""
synthcom = ""
autothink = 0
speedprocessing = 0        # if speed processing is enabled responses
retain2 = ""
retain = ""                # are affected
found = 0
searchset = 1              # what to search for (view code for details)
markerc1 = 0
warning = "Warning! points: "
markerc2 = 0
markerc3 = 0
wordpos = 0
wordc = 0
trade = 0
buy = 0.0
sell = 0.0
a = 0                      # swerg
b = 0
m = 0
procnote = 0
linereq = 0
synthanswer = ""
linecount = 0
finish = 10
anscount = 0
ucount = 0
wordcount = 0
wordcountstat = 0
fail = 0
points = 0
question = 0
structcount = 0
thoughtcount = 0
thought = [""] * 1024      # char thought[1024][512]
structure = [""] * 1024    # char structure[1024][512]
testfile = "test.txt"
lineneeded = ""
file = ""
filenamebuf = ""
word = ""
userinputA = ""
textneeded = ""
notes = ""
fileone = "fileone.txt"
filetwo = "filetwo.txt"
chainreason = ""
synthlogictemp = ""
magic1 = ""
magic2 = ""
magic3 = ""
magic4 = ""
magic5 = ""
magic6 = ""
magic7 = ""
objects = ""
description = ""
actions = ""
desname = desobject = desaction = destime = desdescription = ""
desnumber = desreason = desplace = desemotion = ""
descommand = desbridge = desgame = desconcept = ""
desadj = "desadj"
desadjp = "desadjp"
desadv = "desadv"
desadvtime = "desadvtime"
desprep = "desprep"
desqualities = "desqualities"
desverb = "desverb"
desnameF = desobjectF = desactionF = destimeF = desdescriptionF = ""
desnumberF = desreasonF = desplaceF = desemotionF = ""
descommandF = desbridgeF = desgameF = desconceptF = ""

# Scan mode 0 = intelligent. 1 = skim mode


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


def read_lines(path):
    """Open a file and return its lines (empty list if it cannot be opened)."""
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read().split("\n")
    except OSError:
        return []


def leading_int(s):
    """stringstream(s) >> int"""
    mt = re.match(r"\s*([+-]?\d+)", s)
    return int(mt.group(1)) if mt else 0


# ----------------------------------------------------------------------------
def Config():
    global desname, desnameF, desobject, desobjectF, desaction, desactionF
    global destime, destimeF, desdescription, desdescriptionF
    global desnumber, desnumberF, desreason, desreasonF, desplace, desplaceF
    global desemotion, desemotionF, descommand, descommandF
    global desbridge, desbridgeF, desgame, desgameF, desconcept, desconceptF

    find = -1
    B = ""
    # A = <sha512 serial list, unused: serial check is commented out>
    E = ""

    LINE = 0
    for setup in read_lines("Config.txt"):
        if LINE == 12:
            desname = setup
        if LINE == 13:
            desnameF = setup
        if LINE == 16:
            desobject = setup
        if LINE == 17:
            desobjectF = setup
        if LINE == 0:
            desaction = setup
        if LINE == 1:
            desactionF = setup
        if LINE == 24:
            destime = setup
        if LINE == 25:
            destimeF = setup
        if LINE == 8:
            desdescription = setup
        if LINE == 9:
            desdescriptionF = setup
        if LINE == 14:
            desnumber = setup
        if LINE == 15:
            desnumberF = setup
        if LINE == 20:
            desreason = setup
        if LINE == 21:
            desreasonF = setup
        if LINE == 18:
            desplace = setup
        if LINE == 19:
            desplaceF = setup
        if LINE == 10:
            desemotion = setup
        if LINE == 11:
            desemotionF = setup
        if LINE == 4:
            descommand = setup
        if LINE == 5:
            descommandF = setup
        if LINE == 2:
            desbridge = setup
        if LINE == 3:
            desbridgeF = setup
        if LINE == 22:
            desgame = setup
        if LINE == 23:
            desgameF = setup
        if LINE == 6:
            desconcept = setup
        if LINE == 7:
            desconceptF = setup
        if LINE == 26:
            # C = sha512(setup)
            # find = A.find(C)
            pass
        LINE += 1
    print("Config file loaded.\n")

    while find != -1:
        if find > -1:
            return
        if find == -1:
            # print("Please enter your serial code:")
            # B = input()
            # C = sha512(B)
            # find = A.find(C)
            if find == -1:
                print("\nIncorrect Serial code")
            if find > -1:
                print("Thankyou!")
                with open("Config.txt", "a") as f:
                    f.write(B)
                return
    return


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
    global filenamebuf, k, NCount, space

    filenamebuf = file
    if k == 0:
        # Sout = ""
        pass
    line = ""
    linefull = ""
    pos = -1
    exists = 0

    wordblock = ""
    for line in read_lines(file):
        linefull += line

    if linefull.find(segment) != -1:   # speedhack
        pos = 1
        # print(" conceptual scan:" + segment)

    if pos == 1:
        k += 1
        NCount += 1
        exists = 1
    if pos == -1:
        space += 1
        exists = 0
    line = ""

    if k == 4:
        # Sout += " <-PatternSpace: " + str(space) + " <-Bytes: " + str(NCount)
        space = 0
        k = 0
    return exists


def processlogic(answerstringsegment):
    # linear progression
    # 0 = null, 1 = right, 2 = left, 3 = cross transition
    # 3D progression.
    # 4 = null, 5 = x+, 6 = x-, 8 = y+, 9 = y-, 10 = z+, 11 = z-
    # 4D progression
    # 12 = null, 13 = time +, 14 = time -

    progression = 0
    foo = ""    # (C++: string foo = 0)

    # testcode
    if answerstringsegment.find("are") > 0:
        # progression indicator keyword DB or inet lookup
        progression = 1
    # testcode
    if answerstringsegment.find("aren't") > 0:
        # progression indicator keyword DB or inet lookup
        progression = 1
    # cross domain transfer
    return foo


# MCM (deep learning component) needs processlogic to work!
# algebraic logical processing buffer
def processresponselogic():
    global fail
    fail = 0
    return ""


def processresponsealgbraic(answerstring, userinput):
    global ucount, wordcount, wordcountstat, synthanswer, synthreasonword
    global theanswerreadystatic, Sout, fail

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
        lineend = 0
        lineend = userinput.find(":", lineend + 1)
        while posend != lineend - 1:
            posend = userinput.find(" ", pos + 1)
            word = substr(userinput, pos, posend - pos)
            pos = posend
            if pos == -1:      # guard (C++ would run off the end of the string)
                break
            clip = word.find(" ")
            if clip == 0:
                word = word[1:]

            wordcheck2 = 0
            deviseanswerlimit = answerstringsegment.find(":", wordcheck2)
            while 0 <= wordcheck2 < len(answerstringsegment) - 2:
                wordcheck2 = answerstringsegment.find(word, wordcheck2 + 1)
                if wordcheck2 == -1:
                    break
                deviseanswerpos = answerstringsegment.find(">", wordcheck2)
                deviseanswerlimit = answerstringsegment.find(":", wordcheck2)
                if deviseanswerpos > -1 and deviseanswerlimit > -1:
                    if deviseanswerlimit > deviseanswerpos:
                        theanswer = answerstringsegment[deviseanswerpos + 1:deviseanswerlimit]
                        notexist = userinput.find(theanswer)
                        if notexist == -1:
                            theanswerready = theanswer + " "
            wordcheck = 0

            if trade == 0:
                # wordcheck += filesearch(word, "self.txt")
                wordcheck += filesearch(word, "Command.txt")
                wordcheck += filesearch(word, "bridges.txt")
                wordcheck += filesearch(word, "concept.txt")
                wordcheck += filesearch(word, "objects.txt")
                wordcheck += filesearch(word, "reply.txt")
                wordcheck += filesearch(word, "names.txt")
                wordcheck += filesearch(word, "reason.txt")
                wordcheck += filesearch(word, "time.txt")
                wordcheck += filesearch(word, "places.txt")
                wordcheck += filesearch(word, "emotion.txt")
                wordcheck += filesearch(word, "actions.txt")

                wordcheck += filesearch(word, "descriptions.txt")

                wordcheck += filesearch(word, "Numbers.txt")
                wordcheck += filesearch(word, "adj.txt")
                wordcheck += filesearch(word, "adjpeople.txt")
                wordcheck += filesearch(word, "adv.txt")
                wordcheck += filesearch(word, "advtime.txt")
                wordcheck += filesearch(word, "prep.txt")
                wordcheck += filesearch(word, "qualities.txt")
                wordcheck += filesearch(word, "verbs.txt")
                # get time .
                # get reverse descriptors
                synthcom = ""
                # get word des match
                synthanswer = ""
                if userinput.find("?") == -1:
                    if filesearch(word, "places.txt") == 1:
                        synthanswer = desplace + " is the " + word + "?"
                        synthreasonword = word
                    if filesearch(word, "objects.txt") == 1:
                        synthanswer = desobject + " is " + word + "?"
                        synthreasonword = word
                    if filesearch(word, "actions.txt") == 1:
                        synthanswer = desaction + " does one " + word + "?"
                        synthreasonword = word
                    if filesearch(word, "descriptions.txt") == 1:
                        synthanswer = desdescription + " a " + word + "?"
                        synthreasonword = word
                    if filesearch(word, "reason.txt") == 1:
                        synthanswer = desreason + " does one " + word + "?"
                        synthreasonword = word
                    if filesearch(word, "names.txt") == 1:
                        synthanswer = desobject + " does " + word + " do" + "?"
                        synthreasonword = word

                if wordcheck > 0:
                    wordcountstat += 1
                if question > -1:
                    if wordcheck > 0:
                        wordcount += 1
                        check = answerstringsegment.find(word)
                        if check > -1:
                            completion += 1

        if answered == 0 or answered == 1:
            if completion == wordcount and wordcount > 0:
                theanswerreadyreal += theanswerready + " "
                theanswerreadystatic = theanswerready + " "
                answered = 1
                Sout += "->" + theanswerready
            if completion != wordcount and wordcount > 0:
                fail = 1
                # logic (todo)
                # foo = processlogic(answerstringsegment)

    return theanswerreadyreal


def processlanguage(userinput):
    global markerc1, markerc2, markerc3, anscount, question
    global wordpos, wordc, buy, sell, found, notes
    global magic3, description

    answerstring = ""

    markerc1 = 0
    markerc2 = 0
    markerc3 = 0
    pos = 0
    posend = 0
    lineend = 0
    exists = 1
    anscount = 0
    userinputstack = ""
    userinputstack = userinputstack + userinput

    question = userinput.find("?")
    if question == -1:
        lineend = userinput.find(":", lineend + 1)
        answerstring = answerstring + "[:"
        while posend != lineend - 1:
            posend = userinput.find(" ", pos + 1)
            word = substr(userinput, pos, posend - pos)
            pos = posend
            if pos == -1:      # guard (C++ would run off the end of the string)
                break
            clip = word.find(" ")
            if clip == 0:
                word = word[1:]

            # hardcode md5 / filter.txt check (disabled in original)

            if trade == 1:
                if searchset == 0:
                    for line in read_lines(filetwo):
                        wordpos = 0
                        wordc = 0
                        while wordpos != -1:
                            wordpos = line.find(" ", wordpos + 1)
                            # wordc += 1
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
                                # notes, get sentence

            if trade == 0:
                # (the original repeats one block per lexicon file; same order here)
                lexicons = [
                    ("Command.txt",     descommand),
                    ("concept.txt",     desconcept),
                    ("bridges.txt",     desbridge),
                    ("Numbers.txt",     desnumber),
                    ("names.txt",       desname),
                    ("time.txt",        destime),
                    ("reason.txt",      desreason),
                    ("places.txt",      desplace),
                    ("emotion.txt",     desemotion),
                    ("actions.txt",     desaction),
                    ("descriptions.txt", desdescription),
                    ("objects.txt",     desobject),
                    ("adj.txt",         desadj),
                    ("adjpeople.txt",   desadjp),
                    ("adv.txt",         desadv),
                    ("advtime.txt",     desadvtime),
                    ("prep.txt",        desprep),
                    ("qualities.txt",   desqualities),
                    ("verbs.txt",       desverb),
                ]
                for lexfile, requestdescriptors in lexicons:
                    exists = 0
                    exists = filesearch(word, lexfile)
                    if exists == 1:
                        if lexfile == "actions.txt":
                            magic3 = word
                        if lexfile in ("descriptions.txt", "objects.txt"):
                            description = word
                        answerstring = answerstring + requestdescriptors + ">" + word + ":"
                        anscount += 1
            word = ""
        answerstring += "]"
    return answerstring


# processsentence
# NOTE: SYNTAXEXTRACTOR, GETPREPOSITION, DATAACTIVATOR, RESPONSEINITPROCESSOR
# and SYNTAXBRANCHER are commented out in the original source and therefore
# omitted from this port.


def processKnowledge(userinput, knowledgebase):  # add select knowledgebase
    global desnumber, desobject, destime, desdescription, desreason, desplace
    global desemotion, desaction, descommand, desbridge, desconcept
    global ucount, wordcountstat, speedprocessing, trade, sweep_dummy
    global a, b, m, procnote, notes, chainreason, objects, synthcom
    global buy, sell, found, question, fail

    userinputall = ""
    answerstring = ""
    theanswerready = ""
    sweep = 0
    n = 0
    desnumber = "count"
    desobject = "what"
    destime = "when"
    desdescription = "describe"
    desreason = "why"
    desplace = "where"
    desemotion = "feel"
    desaction = "how"
    descommand = "command"
    desbridge = "bridge"
    desconcept = "concept"
    sentstruc = 0

    while 0 == 0:
        line = ""
        ucount = 0
        wordcountstat = 0
        try:
            with open(knowledgebase, "rb") as fh:
                answerstring = fh.read().decode("latin-1")
        except OSError:
            pass

        if sweep == 0:
            speedprocessing = 0

        if userinput == "load file":
            if Argc == 1:
                userinputall = loadfile("test.txt")
            if Argc > 1:
                userinputall = loadfile(Argv)
            speedprocessing = 1
            userinput = ""
            sweep = 1

        if userinput == "open new window":
            # system("start main.exe")
            pass

        if userinput == "show answerstring":
            userinput = ""
            print(" Z=" + answerstring, end="")

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
                userinput = "you want " + linei
                userinput = userinput + " :"
                answerstring += processlanguage(userinput)
            for linei in read_lines("self.txt"):
                userinput = "you are " + linei
                userinput = userinput + " :"
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
            while 0 == 0:
                print("ERROR")

        if userinput == "E41B":
            userinput = ""
            userinputall = ""
            answerstring = ""
            globals()["textneeded"] = ""
            globals()["lineneeded"] = ""
            notes = ""
            line = ""
            globals()["word"] = ""

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
            # system("start main \"web.txt\"")
            pass

        if userinput == "show userinputall":
            userinput = ""
            print(userinputall, end="")
            m += 1

        if userinput == "show reasonchain":
            print(chainreason, end="")

        if userinput == "think":
            structposA = 0
            thoughtposA = 0
            x = 0
            y = 0
            structurestr = structure[x]
            thoughtstr = thought[y]
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
            # system("main \"auto.txt\"")
            pass

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
            if procnote == 0:
                pass
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
                # (original wrote answerstring to an unopened ofstream: no-op)
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
        if question == -1:
            if trade != 1:
                # print("[" + str(anscount) + " out of " + str(ucount) + " words in sentence recognised]")
                pass
        if fail == 1:
            # theanswerready = processresponselogic()
            pass

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
        # chainrecogniseend:

        if numresp < 200 and numresp > 0:
            x = 1
            for respline in read_lines("response.txt"):
                if x == numresp:
                    print(respline)
                x += 1

        if speedprocessing == 1:
            with open(knowledgebase, "a") as textfile4:
                textfile4.write(answerstring)
        n += 1

        if points < 0:
            # warning2(points)
            pass

        theanswerready2 = synthanswer
        # self question descriptor algo or programmable inference
        # who is in the x? describe the x? what drinks are in the x? command
        # object to self / self to object / self to idea / idea to self
        # des to self / self to des
        if userinput.find(descommand) != -1:
            for line in read_lines("objects.txt"):
                pos = userinput.find(line)
                if pos != -1:
                    objects = line

            synthcom = theanswerready + " " + objects
            # system(synthcom)
            print("\n" + synthcom)

        return theanswerready


def main():
    global Argc, Argv, filename, logout, Sout

    count1 = 0
    if os.name == "nt":
        os.system("color 79")
    presentthought = ""
    AIControlLogic = "I II III O"
    AIControlLogicDefinitions = ":First Person:Second Person:world:cycle repeat:"
    AIEthics = "DHH DHM"
    AIEthicsDefinitions = ":Do not harm any human:Do not harm myself:do not make weapons:"
    AIMandates = "EP CD ISL"
    AIMandatesDefinitions = "{End poverty}{Cure disease}{Improve standard of living}{learn}"
    # ($universe/system) Control logic (causality, space, time, protocol etc..)
    # one(self) person sim, Two(self included) person sim, world sim, cycle.
    # AI ethics incorporates decision retardants when any set ethic is violated.
    # AI mandates ensure the artificial intelligence has at least one purpose.
    phase = 0
    Argc = len(sys.argv)
    if Argc > 1:
        Argv = sys.argv[1]

    # ----------------------------Cognition-------------------------------------
    # once cognition stage is reached, free access to the program components is
    # allowed logically, componentify basic code for easy access (TODO much later...)
    # 3 mechanism systems // consciousness ~opcode processing
    # 5 programmable distinction systems
    # 4 recognition systems
    # 2 logic generation
    # reference body (psychology for starters)
    # (the large commented-out "Begin:" cycle from the original is omitted)

    print("SynthReason 0.9N (BiConsciousSymmetricalProcessor)- Beta - "
          "George Wagenknecht - Jan 2017")
    processToolprev = ""
    Config()
    word1 = ""

    AGE = 0
    ent = 5

    processObject = ""
    key = ""
    processTool = ""
    processTool = input("\nInitilise KnowledgeBase:")

    while 0 == 0:
        joined = ""
        # logic system basic representation // basic story
        processObject = ""
        key = ""

        ent = 7
        filename = processTool + "-" + key + "?.txt"

        with open("logout.txt", "a") as logout:
            logout.write("Initiating Lexeme Processor:\n")

        processToolprev = processTool
        with open("status.txt", "w"):
            pass
        CC = ""

        s1 = 0
        s2 = 0
        C = ""
        Core = ",mind,RDB2,thought,subconscious,feedback,stimulus,live,explore,space,expanse,conscious,"

        desstructarray = ["describe", "how", "when", "who", "what", "count", "why",
                          "where", "feel", "command", "bridge", "game", "concept"]
        SentStruct = ["desadj", "desadjp", "desadv", "desadvtime", "desprep",
                      "desqualities", "desverb"]
        structarray = ["desverb", "describe", "desqualities"]
        J = 0
        Core = ",conscious,"
        newrequest = ""
        Q = 0
        loop = 0

        key = input("\nContext:")
        Logicthinkdescribe = "describe " + key + "?"
        while 0 == 0:

            if processTool == "thought":
                aa = ""
                for a_ in read_lines("RDB2"):
                    aa += a_
                with open("memory", "a") as qq:
                    qq.write(aa)
                with open("RDB2", "w"):
                    pass

            # CORE PROTECTION
            # ------------------------------------------------------------------
            s1 = Core.find(",", s1)
            s2 = Core.find(",", s1 + 1)
            # processTool = Core[s1 + 1:s2]

            with open("logout.txt", "a") as logout:
                logout.write(processToolprev + " ==> " + processTool + "\n")
            filename = processTool + "-" + key + "?.txt"

            xoxo = ""
            newrequest += xoxo + " "
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
            length1 = 0
            length2 = 0
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
                D = E = F = ""
                start = length2
                if start < 0:       # keep find() positions sane (C++ npos wrap)
                    start = 0

            key = word1

            Q = 1
            print(word1 + " ", end="")
            # ------------------------------------------------------------------

            if CC != NE and processTool == "conscious" and processTool != "RDB2":
                # print("\nStability error!")
                pass

            if processTool == "conscious":
                CC = ""

            if loop == 6:
                break
            loop += 1


# free will

if __name__ == "__main__":
    main()
