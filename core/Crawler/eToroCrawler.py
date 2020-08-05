from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Exceptions.LeverageNotAvailable import LeverageNotAvailable
import chromedriver_binary
import time
import logging
import yaml

class eToroCrawler():

    def __init__(self):
        """
        Constructor for the class eToroWrapperServer. It opens a browser tab and calls setup() method to log in the eToro Web IDE
        """
        chrome_options = webdriver.ChromeOptions();
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("window-size=1400,1500")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("enable-automation")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-dev-shm-usage")

        script = '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
            '''
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
        self.mode = "real"
        self.setup()

    def setup(self):
        """
        Logs in the eToro Web IDE
        """
        self.driver.get ("https://www.etoro.com/es/login")
        with open('config.yaml') as config:
            accounts = yaml.load_all(config)
            for account in accounts:
                for id, data in account.items():
                    username = data[0]['username']
                    password = data[1]['password']
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "username"))).send_keys(username)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_tag_name("button").click()

    def get_wallet_info(self):
        """
        Gather user's wallet info

        :return: Raw element which contains the requested information
        :rtype: string
        """
        self.driver.get("https://www.etoro.com/watchlists")
        response = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "footer-wrapp"))).text
        return response

    def get_portfolio(self, active):
        """
        Gather user's portfolio info

        :param active: Its value should be the name of a specific active (btc, ethereum...) or the word general in order to get the general user portfolio. If active is "general" general portfolio view is returned.
        :type active: string

        :return: Raw list which contains the requested information
        :rtype: string
        """
        self.driver.get("https://www.etoro.com/portfolio/"+active)
        n_input = 0
        actives = []
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "ui-table-body")))
        try:
            while True:
                actives.append(self.driver.find_elements_by_class_name("ui-table-row-container")[n_input].text)
                n_input +=1
        except IndexError:
            return str(actives)

    def get_active_info(self, action, active):
        """
        Gather some key data about an active

        :param action: The action type. It can be "buy" or "sell"
        :type action: string
        :param active: Its value should be the name of a specific active (btc, ethereum...) or the word general in order to get the general user portfolio. If active is "general" general portfolio view is returned.
        :type active: string

        :return: Raw dict which contains some specific information about an active
        :rtype: dict
        """
        output = {}
        self.driver.get("https://www.etoro.com/markets/" + active)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "blue-btn"))).click()
        if action == "sell":
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "execution-head-button"))).click()
        output[action + "_price"] = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "execution-main-head-price-value"))).text
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "center-tab"))).click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "risk-itemlevel")))
        leverage = self.driver.find_elements_by_class_name("risk-itemlevel")
        output["available_leverages"] = []
        for option in leverage:
            output["available_leverages"].append(option.text)
        return output

    def set_position_window(self, action, leverage, amount):
        """
        Auxiliary method which refill form fields automatically

        :param action: The action type. It can be "buy" or "sell"
        :type action: string
        :param leverage: Levarage rate
        :type leverage: string
        :param amount: Active amount
        :type amount: string

        :raises LeverageNotAvailable: This exception is raised when an unavailable leverage rate is provided

        """
        if action == "sell":
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "execution-head-button"))).click()
            #self.driver.find_element_by_class_name("execution-head-button").click()
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "center-tab"))).click()
        #self.driver.find_element_by_class_name("center-tab").click()
        input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "stepper-value")))
        input.click()
        input.send_keys(Keys.CONTROL , 'a')
        input.send_keys(Keys.DELETE)
        input.send_keys(amount)
        self.driver.find_element_by_class_name("execution-button").click()
        leverages = self.driver.find_elements_by_class_name("risk-itemlevel")
        pos = 0
        for option in leverages:
            if option.text == leverage:
                self.driver.find_elements_by_class_name("risk-itemlevel")[pos].click()
                break
            pos+=1
        if option.text != leverage:
            raise LeverageNotAvailable(leverage)


    def open_position(self, action, active, leverage, amount):
        """
        This method enables opening a new position

        :param action: The action type. It can be "buy" or "sell"
        :type action: string
        :param active: Name used for an active in the eToro Web IDE.
        :type active: string
        :param leverage: Levarage rate
        :type leverage: string
        :param amount: Active amount
        :type amount: string
        """
        self.driver.get("https://www.etoro.com/markets/" + active)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "blue-btn"))).click()
        time.sleep(5)
        self.set_position_window(action, leverage, amount)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "execution-button"))).click()

    def close_position(self, active, id):
        """
        This method enables closing an existing position.

        :param active: Name used for an active in the eToro Web IDE.
        :type active: string
        :param id: Current id for the target position.
        :type id: int

        """
        self.driver.get("https://www.etoro.com/portfolio/" + active)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "stop")))
        self.driver.find_elements_by_class_name("stop")[id].click()
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "red"))).click()

    def close_all_active(self, active):
        """
        This method enables closing all existing positions of a provided active

        :param active: Name used for an active in the eToro Web IDE.
        :type active: string

        """
        self.driver.get("https://www.etoro.com/portfolio/" + active)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "stop")))
        positions = self.driver.find_elements_by_class_name("stop")
        for position in positions:
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "stop")))
            position.click()
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "red"))).click()

    # Realizar mas test
    def close_all(self):
        """
        This method enables closing all existing positions

        :param active: Name used for an active in the eToro Web IDE.
        :type active: string

        """
        self.driver.get("https://www.etoro.com/portfolio/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table-first-name")))
        actives = self.driver.find_elements_by_class_name("table-first-name")
        target = []
        for active in actives:
            target.append(active.text)
        for active in target:
            print(active)
            self.close_all_active(active)

    def change_mode(self, mode):
        """
        This method enables changing between "virtual" and "real" mode

        :param mode: Mode you want to change. It can be "virtual" or "real"
        :type mode: string

        """
        if self.mode == mode:
            return
        self.driver.get("https://www.etoro.com/watchlists")
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.TAG_NAME, "et-select"))).click()
        if mode == "virtual":
            self.driver.find_elements_by_css_selector("et-select-body-option")[1].click()
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.toggle-account-button"))).click()
        if mode == "real":
            self.driver.find_elements_by_css_selector("et-select-body-option")[0].click()
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.toggle-account-button"))).click()
        self.mode = mode
