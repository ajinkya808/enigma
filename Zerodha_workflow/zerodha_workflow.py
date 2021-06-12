import pandas as pd
import numpy as np
import xlrd
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import os
import time
import logging
import json

class zerodha_workflow:


    def enter_text(self, element, text):
        element.send_keys(text)

    def __init__(self, operating_dir, chromeDriver_dir):
        
        with open('Login_Credentials.txt') as json_file:
            login_credentials = json.load(json_file)
        
        login_id_zerodha = login_credentials["zerodha_credentials"]["login_id"]
        password_zerodha = login_credentials["zerodha_credentials"]["password"]
        pin_zerodha = login_credentials["zerodha_credentials"]["pin"]

        # Zerodha Webdriver
        if os.path.exists(operating_dir+"/Zerodha_workflow/holdings.csv"):
            os.remove(operating_dir+"/Zerodha_workflow/holdings.csv")
        else:
            pass

        op = webdriver.ChromeOptions()
        p = {"download.default_directory": operating_dir +
             "/Zerodha_workflow", "safebrowsing.enabled": "false"}
        op.add_experimental_option("prefs", p)
        driver = webdriver.Chrome(executable_path=chromeDriver_dir, options=op)
        driver.implicitly_wait(3)

        driver.get("https://kite.zerodha.com/")
        driver.maximize_window()
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[1]/div/div/div/form/div[2]/input").send_keys(login_id_zerodha)  # Login ID for trendlyn
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[1]/div/div/div/form/div[3]/input").send_keys(password_zerodha)  # Password
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[1]/div/div/div/form/div[4]/button").click()  # submit click
        # driver.find_element_by_xpath(
        #     "/html/body/div[1]/div/div/div[1]/div/div/div/form/div[2]/div/input").send_keys(pin_zerodha)  # pin zerodha
        try:
            twofa_field=driver.find_element_by_id("pin")
            assert twofa_field.is_displayed()
            self.enter_text(twofa_field,pin_zerodha)
        except Exception:
            totp=input("Two Factor Authentication enabled for this account. Please enter Authentication code from your authorized authenticator app:\n->")
            twofa_field=driver.find_element_by_id("totp")
            assert twofa_field.is_displayed()
            self.enter_text(twofa_field, totp)
        submit_button=driver.find_element_by_class_name("button-orange")
        assert submit_button.is_displayed()
        submit_button.click()
        
        driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[1]/div/div/div/form/div[3]/button").click()  # continuebutton
        driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div/div[2]/div[1]/a[3]/span").click()  # click on holdings
        driver.find_element_by_xpath(
            "/html/body/div[1]/div[2]/div[2]/div/div/section/div/div/div/span[3]/span").click()  # click on download
        time.sleep(2)
        logging.info('File download successful')
        driver.quit()

        # Read Zerodha Sheet
        zerodha_holdings = pd.read_csv(
            operating_dir+"/Zerodha_workflow/holdings.csv", usecols=[0, 1, 2, 3])

        # Read upload document to trendline
        upload_document = pd.read_excel(
            operating_dir+"/Zerodha_workflow/bulk_add_wl.xls")
        upload_document['Stock code'] = zerodha_holdings['Instrument']
        upload_document.to_excel(
            operating_dir+"/Zerodha_workflow/bulk_add_wl.xls", index=False)
