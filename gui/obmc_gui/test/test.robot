*** Settings ***
Library           Selenium2Library
Library  XvfbRobot

*** Variables ***
${URL}          https://www.google.com
${BROWSER}      Firefox


*** Keywords ***
Open Browser To Login Page
        Start Virtual Display  1920  1080
        Open Browser   ${URL}           ${BROWSER}
        Set Window Size  1920  1080

*** Test Cases ***
Test Case 1
        Open Browser To Login Page
