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

DetailsHead = ["Name", "Coupon", "Maturity", "Finra Symbol"]
BondData = []
FirstRun = True
#csv_reader = ["KILIMANJARO II RE LTD", "SECTOR RE V LTD", "KILIMANJARO II RE LTD."]

with open('Search_Results/Issuer_Search_Input.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    next(csv_reader)
    for row in csv_reader:
        IssuerName = row[0]
        link = 'http://finra-markets.morningstar.com/BondCenter/Default.jsp'
        driver.get(link)  # visit the link

        search = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="TabContainer"]/div/div[1]/div[2]/ul/li[3]/a/span')))  #
        search.click()
        inputBond = driver.find_element_by_xpath('//*[@id="firscreener-issuer"]')
        inputBond.send_keys(IssuerName)  # input
        showResults = driver.find_element_by_xpath('//*[@id="ms-finra-advanced-search-form"]/div[2]/input[2]')
        showResults.click()

        if FirstRun == True:
            time.sleep(2)
            agree = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH,
                                                                                   '//*[@id="ms-agreement"]/input')))  # driver.find_element_by_xpath('//*[@id="ms-agreement"]/input')
            agree.click()
            FirstRun = False

        time.sleep(2)
        try:
            totalPages = driver.find_element_by_xpath('//*[@id="ms-finra-search-results"]/div/div[3]/div[2]/div[2]/div/span').text.split(' ')[1]

        except:
            driver.get(URL)
            time.sleep(2)
            URL = driver.current_url
            params = URL.split('?')[1].split('&')
            ticker = params[0].split("=")[1]
            print("One Bond Found")
            print(ticker)
            URL2 = "http://quotes.morningstar.com/bondquote/quote?t="
            NewURL = URL2 + ticker

            driver.get(NewURL)
            time.sleep(2)

            BondName = driver.find_element_by_xpath('//*[@id="msqt_banner"]/div[1]/div/h1').get_attribute(
                "innerHTML").strip()
            BondMaturity = driver.find_element_by_xpath('//*[@id="market_wrapper"]/div[2]/div').get_attribute(
                "innerHTML").strip()
            BondCoupon = driver.find_element_by_xpath('//*[@id="market_wrapper"]/div[1]/div[1]').get_attribute(
                "innerHTML").strip()
            BondSymbol = driver.find_element_by_xpath(
                '//*[@id="symbol"]/text()').get_attribute("innerHTML").strip()

            details = [BondName] + [BondCoupon] + [BondMaturity] + [BondSymbol]
            print(details)
            BondData.append(details)
            break
            #not tested yet lel

        print('Number of Pages: ', totalPages)
        totalPagesCount = int(totalPages)

        i = 0
        while i <= totalPagesCount:
            if totalPagesCount == 0:
                details = [IssuerName] + ["No Data"]+ ["No Data"]+ ["No Data"]
                print(details)
                BondData.append(details)
                break

            if totalPagesCount != 1:
                nextPage = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'qs-pageutil-next')))
            else:
                nextPage = 0

            NumResults = len(driver.find_elements(By.CLASS_NAME, "rtq-grid-row"))
            print("Number of Results on Page:", NumResults-1, "- Page {}/{}".format(i+1,totalPagesCount))

            for ElementNum in range(1,NumResults):
                BondName = driver.find_element_by_xpath('//*[@id="ms-finra-search-results"]/div/div[3]/div[1]/div[1]/div[2]/div[2]/div/div[{}]/div[2]/div/a'.format(ElementNum)).get_attribute("innerHTML").strip()
                BondSymbol = driver.find_element_by_xpath('//*[@id="ms-finra-search-results"]/div/div[3]/div[1]/div[1]/div[2]/div[2]/div/div[{}]/div[3]/div'.format(ElementNum)).get_attribute("innerHTML").strip()
                BondMaturity = driver.find_element_by_xpath('//*[@id="ms-finra-search-results"]/div/div[3]/div[1]/div[1]/div[2]/div[2]/div/div[{}]/div[6]/div'.format(ElementNum)).get_attribute("innerHTML").strip()
                BondCoupon = driver.find_element_by_xpath('//*[@id="ms-finra-search-results"]/div/div[3]/div[1]/div[1]/div[2]/div[2]/div/div[{}]/div[7]/div'.format(ElementNum)).get_attribute("innerHTML").strip()

                details = [BondName] + [BondCoupon] + [BondMaturity] + [BondSymbol]
                print(details)
                BondData.append(details)

            if nextPage == 0:
                break

            if 'disable' in nextPage.get_attribute('class'):
                break;
            nextPage.click()
            i = i + 1
            time.sleep(3)

    #.format in case I want to make the file naming dynamic (number of runs with a dump file for example)
a = 1
with open('Search_Results/Search_Results_by_Issuer_Name_No{}.csv'.format(a), mode='w+', newline='') as trade_file:
    writer = csv.writer(trade_file, delimiter=';')

    writer.writerow(DetailsHead)
    for d in BondData:
        writer.writerow(d)

    print('Bond_Details_Output/Bond_Details_No{}.csv file created.'.format(a))

driver.close()
end = datetime.now()
TimeNeeded = end - start
print("Finished in: {}".format(TimeNeeded))
