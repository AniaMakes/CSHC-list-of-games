#!/usr/bin/python -tt
# Copyright 2014 - Rob Barton
#
# 13-Aug-2014  Rob Barton            Initial version
# 11-Sep-2014  Rob Barton            Made a first draft work
# 08-Oct-2014  Rob Barton            Add ability to sort and filter on team and date
# 15-Dec-2015  Ania Rygielska & David Bebb  Add ability to guess number of umpires based on previous arrangements
# Sept-2017 Ania Rygielska          Added a list of all the opposing teams (so that it's easy to know which clubs
#                                   to contact about umpire arrangements at the beginning of the season)
# $HISTORY$
#
""" A Python script to convert this seasons hockey fixtures into printable format.  Useful for organising umpires!
    The script connects to the club website's calendar of fixtures and parses this into the various fixtures sorted
    chronologically by default.  The fixtures are output to stdout.

    Each fixture is parsed to capture the date, South team, opposition, venue and start time.  The result is output
    in the format:

        20-Sep   L1 vs Harverhill Ladies 1, Long Road, 10:30 start (? umpires needed)

    Usage:

        hockey [date] [team]

    The optional 'date' argument is of the form 'DD-MMM' (e.g. '08-Nov') or of the form 'MMM' (e.g. 'Nov')
    The optional 'team' argument is the two characters representing gender and team number (e.g. 'L1')

    This powerful combination or arguments allows callers to:
       - print all fixtures on a particular date; these are sorted by team (L1-L3 first then M1-M5)
       - print a specified team only; the fixtures are sorted chronologically
       - print a specified team and date; only one line is printed if there is a fixture
       - print a specified month; fixtures are sorted by date and then by team
       - print a specified team and month; fixtures are sorted by date
       - if no filtering is provided all club fixtures are printed chronologically

    This script returns 0 if successful otherwise a non-zero value.

    How does thsi script work?

    The script expects to see an internet calendar '.ics' format stream from the URL in which fixtures are recorded
    via calendar events in the following format:

        BEGIN:VEVENT
        SUMMARY:[H] L1 vs Haverhill Ladies 1
        DTSTART;VALUE=DATE-TIME:20140920T103000
        DTEND;VALUE=DATE-TIME:20140920T120000
        DTSTAMP;VALUE=DATE-TIME:20140813T212055Z
        UID:http://www.cambridgesouthhockeyclub.co.uk/matches/1573/
        DESCRIPTION:L1 vs Haverhill Ladies 1
        LOCATION:Long Road Sixth Form College\, Long Road\, Cambridge\, CB2 8PX
        URL:http://www.cambridgesouthhockeyclub.co.uk/matches/1573/
        END:VEVENT

    Future enhancements could be to:
       - instantiate a fixture class object and pass that around
       - validate the fixture lines make sense


"""


################################################################################
# List the imports (in alphabetical order)
#
import calendar

import re
import sys
import urllib
import time

##from icalendar import Calendar, Event
##from datetime import datetime
##from icalendar import UTC


################################################################################
# Here are some script globals
#
calendarUrl = r"http://www.cambridgesouthhockeyclub.co.uk/matches/cshc_matches.ics"


################################################################################
# Helper function which opens a URL and returns its "file" if it is a calendar
#
def getUrlFile(urlToUse):
    try:
        urlFile = urllib.urlopen(urlToUse)

        if urlFile.info().gettype() == 'text/calendar':
            return urlFile
        else:
            print "Not a text/calendar URL: " + repr(urlToUse)
            print "This URL is of type: " + repr(urlFile.info().gettype())
            exit (1)

    except IOError:
        print "Unable to read URL: " + repr(urlToUse)
        exit (1)


################################################################################
# Helper function to return True of the match is away, False otherwise
#
def extractIsAway(text):
    match = re.search(r"SUMMARY:\[([HA])\]\s?", text)

    if match and match.group(1) == "A":
        return True

    return False


################################################################################
# Helper function to return the CSHC team name
#
def extractTeam(text):
    match = re.search(r"SUMMARY:\[[HA]\]\s?(\w*)", text)

    if match:
        return match.group(1)

    print "Unable to ascertain team"
    exit (1)


################################################################################
# Helper function to return the opposition team name
#
def extractOpposition(text):
    match = re.search(r"SUMMARY:\[[HA]\]\s?\w*\s?[\S]*\s?(.*)", text)

    if match:
        return match.group(1).rstrip()

    print "Unable to ascertain opposition"
    exit (1)


################################################################################
# Helper function to return the abbreviated month given the nth month
#
def getMonthName(n):
    if n == "01":
        return "Jan"
    elif n == "02":
        return "Feb"
    elif n == "03":
        return "Mar"
    elif n == "04":
        return "Apr"
    elif n == "05":
        return "May"
    elif n == "06":
        return "Jun"
    elif n == "07":
        return "Jul"
    elif n == "08":
        return "Aug"
    elif n == "09":
        return "Sep"
    elif n == "10":
        return "Oct"
    elif n == "11":
        return "Nov"
    elif n == "12":
        return "Dec"

    print "Unable to ascertain month abbreviation"
    exit (1)


################################################################################
# Helper function to return the date
#
def extractDate(text):
    match = re.search("DTSTART;VALUE=DATE-TIME:(\d\d\d\d)(\d\d)(\d\d)T?", text)

    ##  It's possible to have one of two formats for the dates, i.e...
    ##    DTSTART;VALUE=DATE-TIME:20140910T215709Z
    ##    DTSTART;VALUE=DATE:20140906
    ##  This affects extraction of start and end times as well as dates, so if
    ##  we have just a DATE then return "??:??" for the time aspect.
    ##
    if not match:
        match = re.search("DTSTART;VALUE=DATE:(\d\d\d\d)(\d\d)(\d\d)?", text)

    if not match:
        print "Unable to ascertain month abbreviation"
        exit (1)

    monthName = getMonthName(match.group(2))

    return match.group(3) + "-" + monthName


################################################################################
# Helper function to return the start time
#
def extractStart(text):
    match = re.search("DTSTART;VALUE=DATE-TIME:.*T(\d\d)(\d\d)", text)

    if match:
        return match.group(1) + ":" + match.group(2)
    else:
        match = re.search("DTSTART;VALUE=DATE:.*", text)

    if match:
        return "??:??"

    print "Unable to ascertain start time and it is not unknown"
    exit (1)


################################################################################
# Helper function to return the end time
#
def extractEnd(text):
    match = re.search("DTEND;VALUE=DATE-TIME:.*T(\d\d)(\d\d)", text)

    if match:
        return match.group(1) + ":" + match.group(2)
    else:
        match = re.search("DTEND;VALUE=DATE:.*", text)

    if match:
        return "??:??"

    print "Unable to ascertain end time and it is not unknown"
    exit (1)


################################################################################
# Helper function to return the venue
#
def extractLocation(text, isAway):
    if isAway:
        return "Away"

    match = re.search(r"LOCATION:(.*?)\\", text)

    ##  Sometimes the venue is not yet known, so declare that as "TBD", it's not fatal
    if not match:
        return "TBD"

    ##  Now map common home venues to their colloquial names
    rawLocation = match.group(1)

    if rawLocation == "Long Road Sixth Form College":
        return "Long Road"

    if rawLocation == "Cambridge University HC Astro":
        return "Wilberforce Road"

    if rawLocation == "Coldhams Common":
        return "Abbey"

    if rawLocation == "Peter Boizot Astro":
        return "St Catz"

    if rawLocation == "St John's College Sports Ground":
        return "St Johns"

    if rawLocation == "The Leys School":
        return "Leys"

    if rawLocation == "Perse Girls School":
        return "Perse Girls"

    if rawLocation == "Perse Boys School":
        return "Perse Boys"

    return rawLocation

################################################################################
# Helper function to automate how many umpires is needed
#

def umpEach(text):
    opposition =  extractOpposition(text)
    isAway = extractIsAway(text)
    team = extractTeam(text)

    one_list = ["St Ives", "Cambridge City"]
    for opponent in one_list:
        if opponent in opposition:
            return ", 1 umpire needed"
    if isAway:
        return ", 0 umpires needed"
    elif team == "M1":
        return ", 0 umpires needed"
    else:
        return ", 2 umpires needed"

################################################################################
# Helper function to compose the output line given the parsed match data, e.g.
#
#   20-Sep   L1 vs Harverhill Ladies 1, Long Road, 10:30 start (? umpires needed)
#

def composeLine(date, team, opposition, location, start, umpires):
    output = date
    output += "   "
    output += team
    output += " vs "
    output += opposition
    output += ", "
    output += location
    output += ", "
    output += start
    output += " start "
    output += umpires

# (? umpires needed)"

    return output


################################################################################
# Helper function which extracts the next fixture numbers from a line which ends with "nn seconds"
#
def getNextFixture(text):
    isAway = extractIsAway(text)
    team = extractTeam(text)
    opposition = extractOpposition(text)
    date = extractDate(text)
    start = extractStart(text)
    end = extractEnd(text)
    location = extractLocation(text, isAway)
    umpires = umpEach(text)

##     print "Away " + str(isAway)
##     print "Team " + team
##     print "Oppo " + opposition
##     print "Date " + date
##     print "Strt " + start
##     print "End  " + end
##     print "Loca " + location

    line = composeLine(date, team, opposition, location, start, umpires)

    return line

################################################################################
# Small function to sort by the 10th and 11th chars of a line (i.e. the team)
#
def teamSorter(list):
    return list[9:11]


################################################################################
# Small function to sort the output list according to date first and then sort them by team
#
def getSortedLines(outputLines, dateFilter):
    sortedList = outputLines

    if dateFilter == "":
        return outputLines

    ##  If we are given a precise date, e.g. 08-Nov, then just sort by team.
    ##  However, if given a month, e.g. Nov, then sort by team then by date.
    if dateFilter[0].isdigit():
        return sorted(outputLines, key=teamSorter)

    sortedByTeamList = sorted(outputLines, key=teamSorter)
    return sorted(sortedByTeamList)


################################################################################
# Define a main() function
#
def main():
    # Get the name from the command line, using 'World' as a fallback.
    teamFilter = ""
    dateFilter = ""

    if len(sys.argv) >= 2:
        iArg = 1
        while iArg != len(sys.argv):
            ##  If the argument is a team, e.g. M1, L2, etc... then filter by team otherwise assume it's a date filter
            if ((sys.argv[iArg][0] == "M" or sys.argv[iArg][0] == "L") and sys.argv[iArg][1].isdigit()):
                teamFilter = sys.argv[iArg]
            else:
                dateFilter = sys.argv[iArg]
            iArg += 1

    print "Parsing URL : " + repr(calendarUrl)

    urlFile = getUrlFile(calendarUrl)

    fullText = urlFile.read()
    index = 0
    count = 0
    outputLines = []

    opponentsList = []


    ##  Bail out after a thousand fixtures
    while index != -1 and count < 1000:
        count += 1
        startOffset = fullText[index:].find("BEGIN:VEVENT")
        endOffset = fullText[index:].find("END:VEVENT")

        if startOffset == -1:
            break

        line = getNextFixture(fullText[index + startOffset:index + endOffset])

        # once a year useful bit - makes a list of all the opposing teams so that x umpire @ home can be made
        team = extractTeam(fullText[index + startOffset:index + endOffset])
        if team != "M1":
            opponent = extractOpposition(fullText[index + startOffset:index + endOffset])
            teamLen = len(opponent)
            club = opponent[0:teamLen-2]
            opponentsList.append(club)

        if ((teamFilter == "" or str(line).find(teamFilter) != -1) and (dateFilter == "" or str(line).find(dateFilter) != -1)):
            outputLines.append(line)

        index += endOffset + 10


    if count >= 999:
        print "WARNING: Stopping after 1000 fixtures!"

    ##  Only sort the output if dateFilter is set
    sortedLines = getSortedLines(outputLines, dateFilter)

    ##  Printing each line of the list one at a time gives clearer information
    for i in sortedLines:
        print i

    print ("***********************")
    print opponentsList
    opposingClubs = sorted(list(set(opponentsList)))
    print ("List of opposing clubs " + repr(set(opposingClubs)))
    print ("List of opposing clubs " + repr(opposingClubs))


    return 0


################################################################################
# This is the standard boilerplate that calls the main() function.
#
if __name__ == '__main__':
    main()
