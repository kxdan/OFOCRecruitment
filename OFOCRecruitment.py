import urllib3
from bs4 import BeautifulSoup
import requests
import copy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from threading import Thread
from random import randint
#You need to install both Selenium and the appropriate drivers
#Selenium  & Firefox (therefore geckodriver)
USERNAME = "OutOfFocusRecruiter"
PASSWORD = "INSERTHERE"
def findElementsAndBegin():
    keywordsToSearchFor = ['LF', 'SP', 'pilot', 'Pilot']
    browser = webdriver.Firefox()
    browser.get('http://www.reddit.com/r/evejobs')
    print('Getting homepage posts')
    time.sleep(1)
    allElements = []
    allElements = browser.find_elements_by_class_name("title.may-blank")
    elementsToProcess = []
    for element in allElements:
        tempStr = element.text
        if any(ext in tempStr for ext in keywordsToSearchFor):
            elementsToProcess.append(element.get_attribute("href"))
    if len(elementsToProcess) > 0:
        print('Beginning Process, ' + str(len(elementsToProcess)) + " elements found")
        loginFunction(browser)
        replyToLinks(elementsToProcess,browser)
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

findElementsAndBegin()