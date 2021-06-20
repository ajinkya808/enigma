# /usr/bin/python3
# Author: rd

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from cryptography.fernet import Fernet
from config import creds

import os
import time
import pandas as pd

browser=None
fernet=None
crypto_key=None
exclude_watch_list=[0, 5]

def launch_browser():
    global browser
    options = webdriver.ChromeOptions()
    
    p={"download.default_directory": os.path.join(os.getcwd(),"data")}
    options.add_experimental_option("prefs", p)
    browser = webdriver.Chrome("./chromedriver", options=options)

def decrypt_text(text:str):
    global crypto_key
    global fernet
    if not crypto_key or fernet:
        with open("./crypto_key.txt") as key_file:
            crypto_key=key_file.read()
        fernet= Fernet(crypto_key)
        return fernet.decrypt(bytes(text,'utf-8')).decode("utf-8")
    else:
        return fernet.decrypt(bytes(text,'utf-8')).decode("utf-8")


def click(element):
    ActionChains(browser).click(element).perform()

def kill_browser():
    browser.quit()

def enter_text(element, text):
    element.send_keys(text)


def get_wl_instruments():

    def cleanse_instrument_data(text):
        print("Processing instrument text %s",text)
        text=text.replace("BSE", "") if "BSE" in text else text
        text=text.replace("%", "").replace("  ", "\n")
        instrument={}
        split_text=text.split("\n")
        instrument["instrument"]=split_text[0]
        instrument["change"]=split_text[1]
        instrument["cmp"]=split_text[2]

        return instrument
    
    # open browser
    launch_browser()
    
    # visit KITE and get navigate to Watchlist
    browser.get("https://kite.zerodha.com")

    # enter un, pw
    un_field = browser.find_element_by_id("userid");
    assert un_field.is_displayed();
    enter_text(un_field,decrypt_text(creds.get("un")));
    pwd_field = browser.find_element_by_id("password");
    assert pwd_field.is_displayed();
    enter_text(pwd_field,decrypt_text(creds.get("pw")));
    login_button=browser.find_element_by_class_name("button-orange")
    assert login_button.is_displayed()
    click(login_button)
    # ActionChains(browser).click(submit_button).perform()
    time.sleep(3)

    # enter pin
    try:
        twofa_field=browser.find_element_by_id("pin")
        assert twofa_field.is_displayed()
        enter_text(twofa_field,decrypt_text(creds.get("pin")))
    except Exception:
        totp=input("Two Factor Authentication enabled for this account. Please enter Authentication code from your authorized authenticator app:\n->")
        twofa_field=browser.find_element_by_id("totp")
        assert twofa_field.is_displayed()
        enter_text(twofa_field, totp)
    submit_button=browser.find_element_by_class_name("button-orange")
    assert submit_button.is_displayed()
    click(submit_button)

    browser.maximize_window()

    time.sleep(2)

    # get watchlist selector
    watchlist_selector=browser.find_element_by_class_name("marketwatch-selector")

    # click settings panel
    settings_button=watchlist_selector.find_elements_by_tag_name("li")[-1]

    settings_button.click()

    time.sleep(2)

    # hide direction
    browser.find_elements_by_class_name("su-checkbox-box")[0].click() if browser.find_elements_by_class_name("su-checkbox")[0].is_selected() else None
    
    # show change
    browser.find_elements_by_class_name("su-checkbox-box")[1].click() if not browser.find_elements_by_class_name("su-checkbox")[1].is_selected() else None

    # hide holdings
    browser.find_elements_by_class_name("su-checkbox-box")[2].click() if browser.find_elements_by_class_name("su-checkbox")[2].is_selected() else None

    # hide settings panel
    settings_button.click()

    time.sleep(1)
    
    #get watchlists
    watchlist_elements=watchlist_selector.find_elements_by_tag_name("li")

    # for each watchlist:
    instrument_collection=[]
    for idx, watchlist_element in enumerate(watchlist_elements):
        if idx not in exclude_watch_list:
            watchlist_element.click()
            time.sleep(2)

            watchlist_num=watchlist_element.text
            # instruments=[]
            # get instruments
            for instrument_element in browser.find_elements_by_class_name("vddl-draggable"):
                time.sleep(1)
                instrument=cleanse_instrument_data(instrument_element.text)
                instrument["watchlist_num"]=watchlist_num
                instrument_collection.append(instrument)
            
            # instrument_collection[watchlist_num]=instruments

    kill_browser()
    return instrument_collection

if __name__=="__main__":
    instruments_collection=get_wl_instruments()
    instruments=pd.DataFrame(instruments_collection)
    instruments.to_csv("watchlist_instruments.csv", index=False, index_label=False, header=True)
    print(instruments)