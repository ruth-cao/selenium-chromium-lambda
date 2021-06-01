import os
import shutil
import uuid
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

logger = logging.getLogger()

class WebDriverScreenshot:
    def __init__(self):
        self._tmp_folder = '/tmp/{}'.format(uuid.uuid4())

        if not os.path.exists(self._tmp_folder):
            os.makedirs(self._tmp_folder)

        if not os.path.exists(self._tmp_folder + '/user-data'):
            os.makedirs(self._tmp_folder + '/user-data')

        if not os.path.exists(self._tmp_folder + '/data-path'):
            os.makedirs(self._tmp_folder + '/data-path')

        if not os.path.exists(self._tmp_folder + '/cache-dir'):
            os.makedirs(self._tmp_folder + '/cache-dir')

    def __get_default_chrome_options(self):
        chrome_options = webdriver.ChromeOptions()

        lambda_options = [
            '--autoplay-policy=user-gesture-required',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-client-side-phishing-detection',
            '--disable-component-update',
            '--disable-default-apps',
            '--disable-dev-shm-usage',
            '--disable-domain-reliability',
            '--disable-extensions',
            '--disable-features=AudioServiceOutOfProcess',
            '--disable-hang-monitor',
            '--disable-ipc-flooding-protection',
            '--disable-notifications',
            '--disable-offer-store-unmasked-wallet-cards',
            '--disable-popup-blocking',
            '--disable-print-preview',
            '--disable-prompt-on-repost',
            '--disable-renderer-backgrounding',
            '--disable-setuid-sandbox',
            '--disable-speech-api',
            '--disable-sync',
            '--disk-cache-size=33554432',
            '--hide-scrollbars',
            '--ignore-gpu-blacklist',
            '--ignore-certificate-errors',
            '--metrics-recording-only',
            '--mute-audio',
            '--no-default-browser-check',
            '--no-first-run',
            '--no-pings',
            '--no-sandbox',
            '--no-zygote',
            '--password-store=basic',
            '--use-gl=swiftshader',
            '--use-mock-keychain',
            '--single-process',
            '--headless']

        #chrome_options.add_argument('--disable-gpu')
        for argument in lambda_options:
            chrome_options.add_argument(argument)          
        chrome_options.add_argument('--user-data-dir={}'.format(self._tmp_folder + '/user-data'))
        chrome_options.add_argument('--data-path={}'.format(self._tmp_folder + '/data-path'))
        chrome_options.add_argument('--homedir={}'.format(self._tmp_folder))
        chrome_options.add_argument('--disk-cache-dir={}'.format(self._tmp_folder + '/cache-dir'))
        chrome_options.add_argument('--user-agent=Chrome/90')

        chrome_options.binary_location = "/opt/bin/chromium" 

        return chrome_options      

    def __get_correct_height(self, url, width=1280):
        chrome_options=self.__get_default_chrome_options()
        chrome_options.add_argument('--window-size={}x{}'.format(width, 1024))
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(url)
        height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight )")
        driver.quit()
        return height

    def save_screenshot(self, url, email, pwd, filename, width=1280, height=None):
        if height is None:
            height = self.__get_correct_height(url, width=width)

        chrome_options=self.__get_default_chrome_options()
        chrome_options.add_argument('--window-size={}x{}'.format(width, height))
        chrome_options.add_argument('--hide-scrollbars')

        driver = webdriver.Chrome(chrome_options=chrome_options)
        logger.info('Using Chromium version: {}'.format(driver.capabilities['browserVersion']))
        driver.get(url)

        user = driver.find_element_by_id("j_username")
        user.send_keys(email)

        password = driver.find_element_by_id("j_password")
        password.send_keys(pwd)
        password.send_keys(Keys.RETURN)

        try:
            form = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.NAME, "frmHome"))
            )
            
            driver.get("https://parents.genesisedu.com/ftlee/parents?tab1=studentdata&tab2=forms&tab3=fill&studentid=29060860&formId=CE0A72E9B67E45DE8FDF5124EF25D83F&action=form")
            driver.find_element_by_xpath("//select[@id='fldQuestion_48159F9B94B2409BAF899C57039D3759_C3E2410FA55F43CA84D9FA6426910A93']/option[text()='Yes']").click()
            update = driver.find_element_by_class_name("saveButton")
            update.click()

            forms = WebDriverWait(driver, 5).until(
                 EC.presence_of_all_elements_located((By.NAME, "cellCenter"))
            )
            
            currentDate = datetime.now().strftime("%m/%d/%Y").lstrip("0").replace(" 0", " ")
            logger.info('result contains the latest date: {}'.format(currentDate in forms[2].get_attribute('innerHTML')))

            driver.save_screenshot(filename)
        finally:
           driver.quit()

    def close(self):
        # Remove specific tmp dir of this "run"
        shutil.rmtree(self._tmp_folder)


 