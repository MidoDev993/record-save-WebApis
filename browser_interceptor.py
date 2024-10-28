"""
Open and configure the browser.
Here opens the page you want to capture
"""

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from datetime import datetime

import webbrowser
import time


class start_browser():

    def __init__(self) -> None:
        self.browser = None
        self.completed = False
        self.websites_visited = set()


    def start(self, proxy_ip:str, proxy_port:int, URL:str, browser:int):
        time.sleep(5)

        #PROXY [IP:PORT] DEFAULT
        if proxy_ip == "":
            proxy_ip = "127.0.0.1"

        if proxy_port == None:
            proxy_port = 8080
        
        
        #CHOOSE A BROWSER            
        #1 - Chrome
        #2 - Edge
        #3 - Firefox
        #4- Safari
        if browser == 0:
            browser = {
                "chrome":1,
                "edge":2,
                "firefox":3
            }.get(webbrowser.get().name.lower())

        try:
            match browser:
                case 1:
                    profile = webdriver.ChromeOptions()
                    profile.add_argument(f"--proxy-server={proxy_ip}:{proxy_port}")
                    self.browser = webdriver.Chrome(options=profile)

                case 2:
                    profile = webdriver.EdgeOptions()
                    profile.add_argument(f"--proxy-server={proxy_ip}:{proxy_port}")
                    self.browser = webdriver.Edge(options=profile)

                case 3:
                    profile = webdriver.FirefoxOptions()
                    profile.set_preference("network.proxy.type", 1)
                    profile.set_preference("network.proxy.http", proxy_ip)
                    profile.set_preference("network.proxy.http_port", proxy_port)
                    profile.set_preference("network.proxy.ssl", proxy_ip)
                    profile.set_preference("network.proxy.ssl_port", proxy_port)
                    self.browser = webdriver.Firefox(options=profile)

                case default:
                    print("Exiting the application")

                    with open("log.txt", "a") as file:
                        file.write(f"[BROWSER][{datetime.now()}]: Browser not found. Exiting the application\n\n")

                    self.completed = True

            if not self.completed:
                self.browser.get(URL)
                self.websites_visited.add(URL)

        except WebDriverException as ex:
            with open("log.txt", "a") as file:
                file.write(f"[BROWSER][{datetime.now()}]: {ex}\n\n")

            try:
                self.browser.quit()
            except:
                pass

            self.completed = True


    def finish(self, timing:int) -> None:
        try:
            if timing > 0:
                for i in range(timing):
                    self.websites_visited.add(self.browser.current_url)
                    time.sleep(1)

            else:
                while True:
                    self.websites_visited.add(self.browser.current_url)
                    time.sleep(1)

            self.browser.quit()

        except:
            try:
                self.browser.quit()
            
            except:
                pass
