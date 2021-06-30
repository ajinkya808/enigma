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

    def click(self, driver, element):
        ActionChains(driver).click(element).perform()


    def __init__(self, operating_dir, chromeDriver_dir):

        self.exclude_watch_list=[0, 5]
        
        with open('Login_Credentials.txt') as json_file:
            login_credentials = json.load(json_file)
        
        login_id_zerodha = login_credentials["zerodha_credentials"]["login_id"]
        password_zerodha = login_credentials["zerodha_credentials"]["password"]
        pin_zerodha = login_credentials["zerodha_credentials"]["pin"]

        # Zerodha Webdriver
        if os.path.exists(os.path.join(operating_dir,"Zerodha_workflow","holdings.csv")):
            os.remove(os.path.join(operating_dir,"Zerodha_workflow","holdings.csv"))
        else:
            pass

        op = webdriver.ChromeOptions()
        p = {"download.default_directory": os.path.join(operating_dir,
             "Zerodha_workflow"), "safebrowsing.enabled": "false"}
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
            "/html/body/div[1]/div[1]/div/div[2]/div[1]/a[3]/span").click()  # click on holdings
        driver.find_element_by_xpath(
            "/html/body/div[1]/div[2]/div[2]/div/div/section/div/div/div/span[3]/span").click()  # click on download
        time.sleep(2)
        logging.info('File download successful')
        driver.quit()

        # Read Zerodha Sheet
        zerodha_holdings = pd.read_csv(os.path.join(
            operating_dir,"Zerodha_workflow","holdings.csv"), usecols=[0, 1, 2, 3])

        # Read upload document to trendline
        upload_document = pd.read_excel(
            os.path.join(operating_dir,"Zerodha_workflow","bulk_add_wl.xls"))
        upload_document['Stock code'] = zerodha_holdings['Instrument']
        upload_document.to_excel(os.path.join(
            operating_dir,"Zerodha_workflow","bulk_add_wl.xls"), index=False)

    def get_wl_instruments(self, operating_dir, chromeDriver_dir):

        def cleanse_instrument_data(text):
            is_event=False
            
            print(f"Processing instrument text {text}")
            text=text.replace("BSE", "") if "BSE" in text else text
            if "EVENT" in text:
                is_event=True
            text=text.replace("%", "").replace("  ", "\n").replace("   ", "\n") 
            split_text=text.split("\n")
            instrument={}
            instrument["instrument"]=split_text[0].replace("EVENT", "")
            instrument["change"]=split_text[1]
            instrument["cmp"]=split_text[2]
            instrument["is_event"]=is_event

            return instrument

        with open('Login_Credentials.txt') as json_file:
                login_credentials = json.load(json_file)
            
        login_id_zerodha = login_credentials["zerodha_credentials"]["login_id"]
        password_zerodha = login_credentials["zerodha_credentials"]["password"]
        pin_zerodha = login_credentials["zerodha_credentials"]["pin"]


        op = webdriver.ChromeOptions()
        p = { "safebrowsing.enabled": "false"}
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

        # enter pin
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
        self.click(driver, submit_button)

        # browser.maximize_window()

        time.sleep(2)

        # get watchlist selector
        watchlist_selector=driver.find_element_by_class_name("marketwatch-selector")

        # click settings panel
        settings_button=watchlist_selector.find_elements_by_tag_name("li")[-1]

        settings_button.click()

        time.sleep(2)

        # hide direction
        driver.find_elements_by_class_name("su-checkbox-box")[0].click() if driver.find_elements_by_class_name("su-checkbox")[0].is_selected() else None
        
        # show change
        driver.find_elements_by_class_name("su-checkbox-box")[1].click() if not driver.find_elements_by_class_name("su-checkbox")[1].is_selected() else None

        # hide holdings
        driver.find_elements_by_class_name("su-checkbox-box")[2].click() if driver.find_elements_by_class_name("su-checkbox")[2].is_selected() else None

        # hide settings panel
        settings_button.click()

        time.sleep(1)
        
        #get watchlists
        watchlist_elements=watchlist_selector.find_elements_by_class_name("item")

        # for each watchlist:
        instrument_collection=[]
        for idx, watchlist_element in enumerate(watchlist_elements):
            if idx not in self.exclude_watch_list:
                watchlist_num=watchlist_element.text
                watchlist_element.click()
                time.sleep(2)

                
                # instruments=[]
                # get instruments
                for instrument_element in driver.find_elements_by_class_name("vddl-draggable"):
                    time.sleep(1)
                    instrument=cleanse_instrument_data(instrument_element.text)
                    instrument["watchlist_num"]=watchlist_num
                    instrument_collection.append(instrument)
                
                # instrument_collection[watchlist_num]=instruments

        # kill_browser()
        driver.quit()
        return instrument_collection

if __name__=="__main__":
    zwf=zerodha_workflow(os.getcwd(), os.path.join(os.path.dirname(os.getcwd()), "chromedriver"))
    instruments_collection=zwf.get_wl_instruments(os.getcwd(), os.path.join(os.path.dirname(os.getcwd()), "chromedriver"))
    instruments=pd.DataFrame(instruments_collection)
    instruments.to_csv(os.path.join(
            os.getcwd(),"Zerodha_workflow","watchlist_instruments.csv"), index=False, index_label=False, header=True)
    print(instruments)