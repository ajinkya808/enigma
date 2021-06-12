import pandas as pd 
import numpy as np
import xlrd
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import time
import logging
import json

class trendlyn_workflow:
    def __init__(self,operating_dir,chromeDriver_dir):
        
        

        trendlyn_bulkUpload_sheet_path=operating_dir+"/Zerodha_workflow/bulk_add_wl.xls"
        
        with open('Login_Credentials.txt') as json_file:
            login_credentials = json.load(json_file)
        
        login_id_trendlyn=login_credentials["trendlyne_credentials"]["login_id"]
        password_trendlyne=login_credentials["trendlyne_credentials"]["password"]

        #Trenddlyne Webdriver
        if os.path.exists(operating_dir+"/Trendlyn_workflow/Your Watch List  Performance view - Trendlyne.xlsx"):
            os.remove(operating_dir+"/Trendlyn_workflow/Your Watch List  Performance view - Trendlyne.xlsx")
        else:
            pass

        op = webdriver.ChromeOptions() 
        p = {"download.default_directory":operating_dir+"/Trendlyn_workflow", "safebrowsing.enabled":"false"}
        op.add_experimental_option("prefs", p)
        driver=webdriver.Chrome(executable_path=chromeDriver_dir,options=op)
        driver.implicitly_wait(3)

       


        driver.get("https://trendlyne.com/visitor/loginmodal/")
        driver.maximize_window()
        driver.find_element_by_class_name("close").click() #Close download App card
        #driver.find_element_by_id("login-signup-btn").click() #Login sign up button
        driver.find_element_by_id("id_login").send_keys(login_id_trendlyn) #Login ID for trendlyn
        driver.find_element_by_id("id_password").send_keys(password_trendlyne) #Password
        driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div/div[1]/div/div[1]/div[2]/form/div[3]/button").click() #Login button
        driver.find_element_by_xpath("//*[@id='navbarmoremenu']/li[12]/a").click() #watchlist button
    
        driver.find_element_by_xpath("/html/body/div[2]/div[3]/div[2]/div[1]/div[1]/div/button").click()#select watchlist
        
        driver.find_element_by_xpath("/html/body/div[2]/div[3]/div[2]/div[1]/div[1]/div/ul/li[4]").click()#select ghost
        
        driver.find_element_by_xpath("/html/body/div[2]/div[3]/div[1]/div[2]/div[1]/span[1]/a").click() #bulk upload click
        
        uploadElement = driver.find_element_by_xpath("/html/body/div[2]/div[3]/div[1]/div[2]/div[2]/form/div/div/input")
        uploadElement.send_keys(trendlyn_bulkUpload_sheet_path) #upload sheet to bulkupload
        
        #time.sleep(2)
        driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[1]/div[2]/div[2]/form/div/div/div[1]/button').click() #upload button click
    
        driver.find_element_by_xpath("/html/body/div[2]/div[2]/a").click() #go back button click
        
        #driver.find_element_by_xpath("/html/body/div[2]/div[3]/div[2]/div[1]/div[1]/div/button").click()#select watchlist
        #driver.find_element_by_xpath("/html/body/div[2]/div[3]/div[2]/div[1]/div[1]/div/ul/li[3]").click()#select ghost
        
        driver.find_element_by_xpath("/html/body/div[2]/div[3]/div[2]/div[1]/div[1]/div/button").click()#select watchlist
        driver.find_element_by_xpath("/html/body/div[2]/div[3]/div[2]/div[1]/div[1]/div/ul/li[4]").click()#select ghost
        
        driver.find_element_by_xpath("/html/body/div[2]/div[4]/div/div[2]/div/div[1]/div[2]/ul/li[2]/div/a").click()
        driver.find_element_by_xpath("//*[@id='5002']").click()
        driver.find_element_by_xpath("//*[@id='groupTable_wrapper']/div[1]/div[1]/div[2]/button").click()
        driver.find_element_by_xpath("/html/body/div[2]/div[4]/div/div[4]/div/div[1]/div[1]/div[2]/div/a[2]").click()
        time.sleep(10)
    
        driver.quit()
    
        