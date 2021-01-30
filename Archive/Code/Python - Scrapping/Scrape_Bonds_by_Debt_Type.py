from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
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

link = 'http://finra-markets.morningstar.com/BondCenter/Default.jsp'
driver.get(link)  # visit the link

Search = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="TabContainer"]/div/div[1]/div[2]/ul/li[3]/a/span')))
Search.click()
AdvSearch = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ms-finra-advanced-bond-search"]/h2/a')))
AdvSearch.click()
DebtDropdown = Select(driver.find_element(By.XPATH, '//*[@id="ms-finra-advanced-bond-search"]/div/ul[2]/li[6]/select'))
DebtDropdown.select_by_visible_text("Insurance Linked Security")
showResults = driver.find_element_by_xpath('//*[@id="ms-finra-advanced-search-form"]/div[2]/input[2]')
showResults.click()

agree = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH,'//*[@id="ms-agreement"]/input')))  # driver.find_element_by_xpath('//*[@id="ms-agreement"]/input')
agree.click()
time.sleep(2)

totalPages = driver.find_element_by_xpath('//*[@id="ms-finra-search-results"]/div/div[3]/div[2]/div[2]/div/span').text.split(' ')[1]
print('Number of Pages: ', totalPages)
totalPagesCount = int(totalPages)
x = 0
i = 0
while i <= totalPagesCount:
    nextPage = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'qs-pageutil-next')))

    NumResults = len(driver.find_elements(By.CLASS_NAME, "rtq-grid-row"))
    print("Number of Results on Page:", NumResults - 1, "- Page {}/{}".format(i + 1, totalPagesCount))
    x = x + (NumResults - 1)

    for ElementNum in range(1, NumResults):
        BondName = driver.find_element_by_xpath(
            '//*[@id="ms-finra-search-results"]/div/div[3]/div[1]/div[1]/div[2]/div[2]/div/div[{}]/div[2]/div/a'.format(
                ElementNum)).get_attribute("innerHTML").strip()
        BondSymbol = driver.find_element_by_xpath(
            '//*[@id="ms-finra-search-results"]/div/div[3]/div[1]/div[1]/div[2]/div[2]/div/div[{}]/div[3]/div'.format(
                ElementNum)).get_attribute("innerHTML").strip()
        BondMaturity = driver.find_element_by_xpath(
            '//*[@id="ms-finra-search-results"]/div/div[3]/div[1]/div[1]/div[2]/div[2]/div/div[{}]/div[6]/div'.format(
                ElementNum)).get_attribute("innerHTML").strip()
        BondCoupon = driver.find_element_by_xpath(
            '//*[@id="ms-finra-search-results"]/div/div[3]/div[1]/div[1]/div[2]/div[2]/div/div[{}]/div[7]/div'.format(
                ElementNum)).get_attribute("innerHTML").strip()

        details = [BondName] + [BondCoupon] + [BondMaturity] + [BondSymbol]
        print(details)
        BondData.append(details)

    if 'disable' in nextPage.get_attribute('class'):
        break;
    nextPage.click()
    i = i + 1
    time.sleep(3)

with open('Search_Results/All_ILS_FINRA_Bonds2.csv', mode='w+', newline='') as trade_file:
    writer = csv.writer(trade_file, delimiter=';')

    writer.writerow(DetailsHead)
    for d in BondData:
        writer.writerow(d)

    print('All_ILS_FINRA_Bonds.csv file created.')

driver.close()
end = datetime.now()
TimeNeeded = end - start
print("Total Number of Bonds: ",x)
print("Finished in: {}".format(TimeNeeded))
