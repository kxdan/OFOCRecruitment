import urllib3
from bs4 import BeautifulSoup
import requests
import copy
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
USERNAME = "OutOfFocusRecruiter"
PASSWORD = "recruiter62"
NUMBEROFPAGESTOPROCESS = 3
def findElementsAndBegin():
    keywordsToSearchFor = ['LF', 'SP', 'pilot', 'Pilot', 'LFC']
    browser = webdriver.Firefox()
    allElements = []
    elementsToProcess = []
    currentPageNumber = 0
    browser.get('http://www.reddit.com/r/evejobs')
    print('Getting homepage posts, page number ' + str(currentPageNumber))
    time.sleep(1)
    for currentPageNumber in range (0, NUMBEROFPAGESTOPROCESS):
        allElements = browser.find_elements_by_class_name("title.may-blank")
        # go through multiple pages searching for stuff
        for element in allElements:
            tempStr = element.text
            if any(ext in tempStr for ext in keywordsToSearchFor) and ("pilots" not in tempStr):
                elementsToProcess.append(element.get_attribute("href"))
        nextButton = browser.find_element_by_class_name("next-button")
        nextButton.click()
        time.sleep(3)
    if len(elementsToProcess) > 0:
        print('Beginning Process, ' + str(len(elementsToProcess)) + " elements found")
        loginFunction(browser)
        replyToLinks(elementsToProcess, browser)
        browser.close()
        print('Finished.')


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

def havePostedBefore(browser):
    postersOnThread = []
    postersOnThread = browser.find_elements_by_class_name("author.may-blank")
    for poster in postersOnThread:
        if USERNAME in poster.text:
            return True
    return False

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
            #element.click()
            # Trigger Eve login
            #browser.findElement(By.xpath("//a[text()='Login']")).click()


findElementsAndBegin()
#bumpEveForum()