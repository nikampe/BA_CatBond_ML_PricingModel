from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time, csv
from datetime import datetime

start = datetime.now()

ua = UserAgent()
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (ua.random)
service_args = ['--ssl-protocol=any', '--ignore-ssl-errors=true']
driver = webdriver.Chrome('chromedriver.exe', desired_capabilities=dcap, service_args=service_args)


FirstRun = True
Output = "CUSIP;Ticker;Symbol\n"

with open("Input_CUSIP.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    next(csv_reader)
    for row in csv_reader:
        try:
            cusip = row[0]

            print("CUISP: ", cusip)
            time.sleep(1)

            link = "http://finra-markets.morningstar.com/BondCenter/Default.jsp"
            driver.get(link)  # visit the link
            time.sleep(3)


            search = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="TabContainer"]/div/div[1]/div[2]/ul/li[3]/a')))  #
            search.click()

            inputBond = driver.find_element_by_xpath('//*[@id="firscreener-cusip"]')
            inputBond.send_keys(cusip)
            time.sleep(1)
            showResults = driver.find_element_by_xpath('//*[@id="ms-finra-advanced-search-form"]/div[2]/input[2]')
            showResults.click()
            time.sleep(3)

            if FirstRun == True:
                #disclaimer = 'http://finra-markets.morningstar.com/BondCenter/UserAgreement.jsp'
                #driver.get(disclaimer)
                time.sleep(2)
                agree = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH,
                                                                                       '//*[@id="ms-agreement"]/input')))  # driver.find_element_by_xpath('//*[@id="ms-agreement"]/input')
                agree.click()
                time.sleep(2)
                FirstRun = False

            URL = driver.current_url
            print("URL: ", URL)
            params = URL.split('?')[1].split('&')
            ticker = params[0].split("=")[1]
            symbol = params[1].split("=")[1]

            print("ticker: ", ticker)
            print("symbol: ", symbol)
            Output = Output + (u"{};{};{}\n".format(cusip,ticker,symbol))

        except Exception as e:
            Output = Output + (u"{};Error;Error\n".format(cusip))
            print(e)
            continue


f = open("Output_CUSIP.csv", "w")
f.writelines(Output)
f.close()

end = datetime.now()
TimeNeeded = end - start
print("Finished in: {}".format(TimeNeeded))