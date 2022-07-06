#! /usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from sys import stdout
import time
import os
import sys
import logging
from datetime import datetime

log = logging.getLogger().getChild('System')

log.setLevel(logging.DEBUG) # set logger level
logFormatter = logging.Formatter\
("%(asctime)s %(levelname)-8s %(message)s")
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)

if any(var not in os.environ for var in ["OVERLEAF_URL", "OVERLEAF_USERNAME", "OVERLEAF_PASSWORD", "BACKUP_FREQUENCY", "BACKUP_OVERWRITE"]):
    log.error("One or more environment variables are not present. Consult README.md")
    sys.exit(1)

while True:
    dirname = "/backups"
    if os.environ["BACKUP_OVERWRITE"] != "true":
        dirname = dirname + "/" + datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

    opts = webdriver.ChromeOptions()
    prefs = {'download.default_directory' : dirname}
    opts.add_experimental_option('prefs', prefs)
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opts)

    if "http" not in os.environ["OVERLEAF_URL"]:
        log.error("OVERLEAF_URL does not include transport method (https:// or http://)")

    log.info("Starting login process")

    driver.get(os.environ["OVERLEAF_URL"] + ("/" if os.environ["OVERLEAF_URL"][-1] != "/" else "") + 'login')
    time.sleep(4)

    username_form = driver.find_element('name', 'email')
    password_form = driver.find_element('name', 'password')

    username_form.clear()
    username_form.send_keys(os.environ["OVERLEAF_USERNAME"])
    password_form.clear()
    password_form.send_keys(os.environ["OVERLEAF_PASSWORD"])

    submit_button = driver.find_elements(By.CLASS_NAME, "btn-primary")
    submit_button[0].click()
    time.sleep(5)

    log.info("Logged in. Starting downloads")

    download_buttons = selected_option = driver.find_elements(By.XPATH, '//button[@aria-label="Download"]')
    for i in range(len(download_buttons)):
        log.info("Starting download " + str(i+1) + " of " + str(len(download_buttons)))
        download_buttons[i].click()
        time.sleep(1)

    time.sleep(30)

    if int(os.environ["BACKUP_FREQUENCY"]) == 0:
        log.info("Terminating")
        break
    
    log.info("Waiting for next scheduled activation\n")
    time.sleep((int(os.environ["BACKUP_FREQUENCY"]) * 60) - (35 + len(download_buttons)))

    driver.quit()

