from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time, csv
from datetime import datetime

InputFile = "Search_Results/All_ILS - add.csv"
TickerPositionInInputFile = 2
BondDetailsOutputFile = "Bond_Details_Output/Last_Bond_Details_v2.csv"



def ErrorHandler (ticker, error):
    ErrorReport = open('Bond_Details_Output/ErrorReport.csv', mode='a+', newline='')
    writer = csv.writer(ErrorReport, delimiter=';')

    ErrorTime = datetime.now().strftime("%H:%M:%S")
    writer.writerow([ticker, ErrorTime, error])

    print("Error Report has been updated for {} at {}".format(ticker, ErrorTime))

def createURL(ticker):
    try:
        url = 'http://finra-markets.morningstar.com/BondCenter/BondTradeActivitySearchResult.jsp?'
        # ticker=FGM4361059&startdate=09%2F02%2F2019&enddate=09%2F02%2F2019'

        tickerString = "ticker=F" + ticker
        startdate = 'startdate=' + "01%2F01%2F2000"
        enddate = 'enddate=' + "07%2F31%2F2020"

        finalURL = url + tickerString + '&' + startdate + '&' + enddate

        print('Trade Activity URL: ', finalURL)

        return finalURL

    except Exception as e:
        print(e)
        return None

start = datetime.now()

BondName = "i"
ua = UserAgent()
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (ua.random)
service_args = ['--ssl-protocol=any', '--ignore-ssl-errors=true']
driver = webdriver.Chrome('chromedriver.exe', desired_capabilities=dcap, service_args=service_args)



TotalTrades = 0
tradeHistoryURl = []
Ddata = []
DetailsHead = ["Name", "Coupon", "Maturity", "Trades" ,"S&P","Moodys","TRACE","Ticker","CUSIP"]
TAdata = []
TradeHead = ['Date', 'Time', 'Settlement', 'Status', 'Quantity', 'Price', 'Yield', 'Remuneration', 'ATS', ' Modifier',
        '2nd Modifier', 'Special', 'As-Of', 'Side', 'Reporting Party Type', 'Contra Party Type', 'Finra Ticker']
print('Bond Details Header ::', DetailsHead)
print('Trade Activity Header ::', TradeHead)

FirstRun = True

with open(InputFile) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    next(csv_reader)
    for row in csv_reader:
        try:

            FINRA_ticker = row[TickerPositionInInputFile]
            print("Ticker: " + FINRA_ticker)

            URL = "http://quotes.morningstar.com/bondquote/quote?t=F"
            URL_details = URL + FINRA_ticker

            driver.get(URL_details)

            time.sleep(3)
            BondName = driver.find_element_by_xpath('//*[@id="msqt_banner"]/div[1]/div/h1').get_attribute(
                "innerHTML").strip()
            BondMaturity = driver.find_element_by_xpath('//*[@id="market_wrapper"]/div[2]/div').get_attribute(
                "innerHTML").strip()
            BondCoupon = driver.find_element_by_xpath('//*[@id="market_wrapper"]/div[1]/div[1]').get_attribute(
                "innerHTML").strip()
            BondCUSIP = driver.find_element_by_xpath('//*[@id="msqt_summary"]/div[2]/table/tbody/tr[1]/td[2]/span').get_attribute(
                "innerHTML").strip()
            BondRatingSP = driver.find_element_by_xpath('//*[@id="msqt_credit"]/table/tbody/tr[2]/td[2]').get_attribute(
                "innerHTML").strip().split(' ')[0]
            BondRatingM = driver.find_element_by_xpath('//*[@id="msqt_credit"]/table/tbody/tr[1]/td[2]').get_attribute(
                "innerHTML").strip().split(' ')[0]
            BondRatingTG = driver.find_element_by_xpath('//*[@id="msqt_credit"]/table/tbody/tr[3]/td[2]').get_attribute(
                "innerHTML").strip()

            print(" Name: {}\n CUSIP: {}\n Maturity: {}\n Coupon: {}\n Rating: {}/{}/{}".format(BondName,BondCUSIP,BondMaturity,BondCoupon,BondRatingSP,BondRatingM,BondRatingTG))

            tradeHistory = createURL(FINRA_ticker)
            tradeHistoryURl.append(tradeHistory)

            driver.get(tradeHistory)
            time.sleep(3)

            if FirstRun == True:
                agree = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH,
                                                                                       '//*[@id="ms-agreement"]/input')))  # driver.find_element_by_xpath('//*[@id="ms-agreement"]/input')
                agree.click()
                time.sleep(2)
                FirstRun = False


            # get table details
            try:
                table = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="ms-glossary"]/div/table/tbody')))

                totalPages = \
                driver.find_element_by_xpath('//*[@id="ms-glossary"]/div/table/tfoot/tr/td/div/span').text.split(' ')[1]

                # totalPages = driver.find_element_by_class_name('qs-pageutil-total').text.split(' ')[1]
                print('Number of Pages in Search Result: ', totalPages)
                totalPagesCount = int(totalPages)
                i = 0
                BondTrades = 0
                TAdata = []
                while i <= totalPagesCount:
                    if totalPagesCount == 0:
                        NoTradeDetails = [BondMaturity]+ ["12:00:00"] + [BondMaturity] + ["NoTrade"] + [0] + [100] + []+ ["-"]+ []+ ["_"]+ ["_"]+ ["-"]+ ["-"]+ ["-"]+ ["-"]+ ["-"]+ [BondCUSIP] #check
                        TAdata.append(NoTradeDetails)
                        break;
                    nextPage = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'qs-pageutil-next')))

                    # data in table
                    rows = table.find_elements_by_tag_name('tr')
                    print(BondCUSIP + (u" - Number of Results on Page {}/{}: {}".format(i+1,totalPagesCount, len(rows))))
                    for tr in rows:
                        tds = tr.find_elements_by_tag_name('td')
                        rowData = [d.text for d in tds]
                        print(rowData)
                        rd = rowData + [BondCUSIP]
                        #print(rd)
                        TAdata.append(rd)
                        BondTrades = BondTrades + 1

                    # Click Next Button until it is active
                    if 'disable' in nextPage.get_attribute('class'):
                        break;
                    nextPage.click()
                    i = i + 1
                    time.sleep(4)

            except Exception as e:
                print(e)
                print('ERROR: Reading Data Table failed -> ' + FINRA_ticker)
                ErrorHandler(FINRA_ticker,e)

            print(BondName+"_"+BondCUSIP+" - Total Trades: ", BondTrades)
            TotalTrades = TotalTrades + BondTrades
            print("Total Trades so far: ", TotalTrades)

            now = datetime.now()
            runtime = now - start
            print("Program is running for: {} (Start: {} - Current time: {})".format(runtime, start.strftime("%H:%M:%S"), now.strftime("%H:%M:%S")))

            details = [BondName] + [BondCoupon] + [BondMaturity] + [BondTrades] +[BondRatingSP] + [BondRatingM] + [BondRatingTG] + [FINRA_ticker] + [BondCUSIP]
            Ddata.append(details)

            # write trading history to seperate file
            try:
                with open('Trading_Activity_Output/Add/{}_{}.csv'.format(BondName,BondCUSIP), mode='w+', newline='') as trade_file:
                    writer = csv.writer(trade_file, delimiter=';')

                    writer.writerow(TradeHead)
                    for d in TAdata:
                        writer.writerow(d)

                    print('Trading_Activity_Output/Add/{}_{}.csv file created.'.format(BondName,BondCUSIP))
            except Exception as e:
                print(e)
                print('ERROR: Could not create Trading Activity csv for -> ' + FINRA_ticker)
                ErrorHandler(FINRA_ticker, e)

        except Exception as e:
            print(e)
            print("ERROR: Could not scrape Bond Details -> ",FINRA_ticker)
            ErrorHandler(FINRA_ticker, e)
            continue

try:
    #.format in case I want to make the file naming dynamic (number of runs with a dump file for example)
    a = 1
    with open(BondDetailsOutputFile, mode='w+', newline='') as trade_file:
        writer = csv.writer(trade_file, delimiter=';')

        writer.writerow(DetailsHead)
        for d in Ddata:
            writer.writerow(d)

        print('Bond_Details_Output/Bond_Details_No{}-add.csv file created.'.format(a))
except Exception as e:
    print(e)
    print(Ddata)
    print('ERROR: Could not create Bond Deatils csv')

driver.close()
end = datetime.now()
TimeNeeded = end - start
print("Total Number of Trades: ", TotalTrades)
print("Finished in: {}".format(TimeNeeded))








