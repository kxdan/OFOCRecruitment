import urllib3
from bs4 import BeautifulSoup
import requests
import copy
from secrets import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys
import time
import re
from threading import Thread
from random import randint
#You need to install both Selenium and the appropriate drivers
#Selenium  & Firefox (therefore geckodriver)
USERNAME = USERNAME
PASSWORD = PASSWORD
USERNAMEEVE = USERNAMEEVE
PASSWORDEVE = PASSWORDEVE
NUMBEROFPAGESTOPROCESS = 3
keywordsToSearchFor = ['LF', 'SP', 'pilot', 'Pilot', 'LFC', "toon", 'looking for corp', 'looking for wormhole corp', 'Looking for Wormhole corp' , 'Player']
keywordsToAvoid = ['pilots' , 'recruiting']
#Loads the reddit evejobs page, loads all the elements on the respective page and cycles through pages
#For each element on the page, if the flair is either "looking for corp" or the text is something
#odo with a corp, it'll get added, and posted on later on , posts with avoidance keywords are avoided, posts with
#keywords to search for are added, avoidance takes priority

def findElementsAndBegin():
    browser = webdriver.Firefox()

    elementsToProcess = []
    currentPageNumber = 0
    browser.get('http://www.reddit.com/r/evejobs')
    time.sleep(1)
    #Cycle through all the pages finding posts
    for currentPageNumber in range (0, NUMBEROFPAGESTOPROCESS):
        print('Getting homepage posts, page number ' + str(currentPageNumber))
        #Lists containing elements on the page, and flairs on the page, these lists are parallel

        #NEED TO FIX BUG WHERE X HAS NO FLAIR - get the larger div, then title from that, then flair associated with it, if no flair set to blank
        #FIXED, cycle through all Div elements, get title, and set title as flair if flair cannot be found, throws exception if no flair found
        divelements =  browser.find_elements_by_class_name("entry.unvoted")
        allElements = []
        allFlairElements = []
        for element in divelements:
            allElements.append(element.find_element_by_class_name("title.may-blank"))
            try:
                allFlairElements.append(element.find_element_by_class_name("linkflairlabel"))
            except:
                tempElement = element.find_element_by_class_name("title.may-blank")
                allFlairElements.append(tempElement)
                pass
        # go through multiple pages searching for stuff
        flairElement = 0
        #Go through elements list searching for keywords
        for element in allElements:
            tempStr = element.text
            if flairElement < len(allFlairElements):
                flairText = allFlairElements[flairElement].text

            #Check if either keywords are present or flair is looking for corp
            if (checkSearchFor(tempStr) and checkAvoidance(tempStr)) or ("Looking for Corp" == flairText):
                elementsToProcess.append(element.get_attribute("href"))

            flairElement += 1
        #Travel to next page
        nextButton = browser.find_element_by_class_name("next-button")
        nextButton.click()
        time.sleep(3)
    #Begins posting process if elements exist
    if len(elementsToProcess) > 0:
        print('Beginning Process, ' + str(len(elementsToProcess)) + " elements found")
        loginFunction(browser)
        replyToLinks(elementsToProcess, browser)
        browser.close()
        print('Finished.')

#Check none of the keywords are present that must be avoided
def checkAvoidance(tempStr):
    for element in keywordsToAvoid:
        if element.lower() in tempStr.lower():
            return False #Conflict Exists, do not post
    return True #No Conflict Found

#Check element has keywords we want
def checkSearchFor(tempStr):
    if any(ext in tempStr for ext in keywordsToSearchFor):
        return True #Keyword we want to find exists
    return False #No Keyword Found
#Logs into the reddit page or returns already logged in
def loginFunction(browser):
    loginElements = []
    loginElements = browser.find_elements_by_class_name("login-required")
    if (len(loginElements) > 0):
        print('Logging in')
        loginElements = browser.find_element_by_name('user')
        loginElements.send_keys(USERNAME)
        loginElements = browser.find_element_by_name('passwd')
        loginElements.send_keys(PASSWORD + Keys.RETURN)
        time.sleep(1)
    else:
        print('Already logged in')
#Replies to links passed to it, permitting these links have not been previously posted on
def replyToLinks(linksToProcess,browser):
    for element in linksToProcess:
        browser.get(element)
        #changed to not
        if not havePostedBefore(browser):
            print('Posting on: ' + element)
            textElement = browser.find_element_by_name('text')
            # Ok yes i did this as a dictionary for no good reason but felt like it
            stringDict = {1: """If you're interested in wormholes,check out Out Of Focus,
            we're one of the largest wormhole corps in eve and there is always content available,
            we're a great bunch and focus on small gang warfare so every pilot counts. Check out the link below for more info:
            https://www.reddit.com/r/evejobs/comments/4vps5m/odins_ofoc_wh_pvp_corp/""",
            2: """If you're interested in PVP/wormhole space, check out Out Of Focus,
            we're a small gang pvp corp living in wormhole space, currently looking for new pilots to fly with,
            if you're interested check the link below for more information
            https://www.reddit.com/r/evejobs/comments/4vps5m/odins_ofoc_wh_pvp_corp/""",
            3: """Out of Focus is recruiting, and we're looking for pilots like yourself,
            whilst we're a heavily focused PVP corp we do take things quite light hearted and win with a smile,
            or lose with a laugh. We're one of the largest wormhole corps in eve but obviously wormholes being what they are we focus primarily on small gang warfare.
            If you're interested check out the link below or PM one of us in-game https://www.reddit.com/r/evejobs/comments/4vps5m/odins_ofoc_wh_pvp_corp/"""}
            stringToSend = stringDict[randint(1,len(stringDict))]
            textElement.send_keys(stringToSend + Keys.RETURN)
            saveButton = browser.find_element_by_class_name('save')
            saveButton.click()
            if not didPostGoThrough(browser):
                saveButton.click()
            delayInt =  randint(3,11)
            print('Posted. Delaying for ' + str(delayInt) + ' seconds')
            time.sleep(delayInt)
        else:
            print("Already posted on this one, skipping")
#Checks the username has not been posting already on this thread
def havePostedBefore(browser):
    postersOnThread = []
    postersOnThread = browser.find_elements_by_class_name("author.may-blank")
    for poster in postersOnThread:
        if USERNAME in poster.text:
            return True
    return False

#Deals with reddit "you are doing this too much, by delaying and posting after this time has expired"
def didPostGoThrough(browser):
    errorElement = []
    errorElement = browser.find_elements_by_class_name("error.RATELIMIT.field-ratelimit")
    if len(errorElement) > 0:
        errorText = errorElement[0].text
        numberOfMinutes = re.findall(r'\d+', errorText)
        if len(numberOfMinutes) > 0:
            minutesInteger = int(numberOfMinutes[0])
            #Convert minutes to seconds and add half minute threshold
            secondsInteger = (minutesInteger *60) +30
            print("Caught by reddit, waiting " + str(secondsInteger) + " seconds before continuing")
            print("Current Time: " + str(datetime.now()) + " continuing at: "+ str(datetime.now()+ timedelta(seconds = secondsInteger)))
            time.sleep(secondsInteger)
            return False
    return True

#Will visit the eve online forum website and bump the site

#Improvements, find the last time you posts
#Start by finding how many pages there are. Once you know the number of pages, go to the last page, and look if your name is there, if it is look at the date it was last submitted, if its greater than 1 in month or day from current datetime then post
def bumpEveForum():
    #https: // forums.eveonline.com / default.aspx?g = posts & m = 6583336  # post6583336
    browser = webdriver.Firefox()
    #nav pull-right
    browser.get('https://forums.eveonline.com/default.aspx?g=posts&m=6583336#post6583336')
    loginElements = []
    loginElements = browser.find_elements_by_class_name("nav.pull-right")
    #it's looking at the entire thing rather than just the section that you want you need to pull the child elemenets out of it
    for element in loginElements:
        if 'Login' in element.text:
            element.find_element_by_tag_name("a").click()
            time.sleep(2)
            usernameBoxEve = browser.find_element_by_id("UserName")
            passwordBoxEve = browser.find_element_by_id("Password")

            usernameBoxEve.send_keys(USERNAMEEVE)
            passwordBoxEve.send_keys(PASSWORDEVE)

            loginButtonEve = browser.find_element_by_id("submitButton")
            loginButtonEve.click()
            time.sleep(2)
            replyButtonEve =  browser.find_element_by_id("forum_ctl00_PostReplyLink1")
            replyButtonEve.click()
            time.sleep(2)
            replyBoxEve =  browser.find_element_by_id("forum_ctl00_YafTextEditor")
            replyBoxEve.send_keys("Bump")

            postReplyEve = browser.find_element_by_id("forum_ctl00_PostReply")
            postReplyEve.click()
            #element.click()
            # Trigger Eve login
            #browser.findElement(By.xpath("//a[text()='Login']")).click()
findElementsAndBegin()
bumpEveForum()