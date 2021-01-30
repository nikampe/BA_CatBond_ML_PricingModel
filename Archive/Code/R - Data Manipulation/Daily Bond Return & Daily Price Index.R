#Bond Price Index 2 - individual








library(rvest)
library(stringr)
library(tm)
library(dplyr)
library(lubridate)
library(bizdays)
library(ggplot2)
library(scales)
#Price Index Calculations 


AnalysedBond <- "12482PAA4"
#Peril = "U.S. named storm and hurricane"
#Region <- "JP"
StartDate <- "2018-11-08"
EndDate <- "2019-06-08"
StartPrice <- 100



start_time <- Sys.time()

TradingActivity <- data.frame(Date = as.Date("2015-12-30"), AveDailyPrice = 100, DailyVolumn = 1, BondSize = as.integer(1), CUSIP = "Start", BondReturn = 0, BondWeight = 0)
BondDetailsFile <- "Bond Files/BondDetails_export_v6.csv"
BondDetails <- read.csv(BondDetailsFile, header = TRUE, sep = ";")
BondDetails$Issue.Date <- as.Date(BondDetails$Issue.Date, format = "%d.%m.%Y")
BondDetails$Maturity <- as.Date(BondDetails$Maturity, format = "%d.%m.%Y")
BondDetails$Issue.Price <- as.numeric(gsub(",", ".", BondDetails$Issue.Price))
BondDetails$Issue.Volumn <- as.numeric(BondDetails$Issue.Volumn)
BondDetails$Coupon <- as.numeric(gsub(",", ".", BondDetails$Coupon))
BondDetails$CUSIP <- as.character(BondDetails$CUSIP)
BondDetails$Principle.Reduced <- as.character(BondDetails$Principle.Reduced)


#Select Peril
BondDetails <- BondDetails[BondDetails$Wildfire == TRUE, ]
#BondDetails <- BondDetails[BondDetails$Risk.Category.simplified == Peril,]
#BondDetails <- BondDetails[(BondDetails$Region.covered == "JP"),]
BondDetails <- BondDetails[!(BondDetails$CUSIP == AnalysedBond),]



#Reading the required trading histories
TradingFiles <- c()
for (i in 1:length(BondDetails$Issuer)){
  TradingFiles <- c(TradingFiles, paste(BondDetails$Issuer[i],BondDetails$CUSIP[i], sep = "_"))
}


#Replacing the capped trade sizes
OneMM <- "1000000"
FiveMM <- "5000000"

cal <-  create.calendar(name = "mycal", weekdays=c("saturday", "sunday"), start.date = "2000-12-31" ,end.date = "2030-07-31")


TFileLink <- paste(paste("Bond Files/Trading_Activity/", TradingFiles[],sep = ""), ".csv",sep = "")

for (g in 1:length(TradingFiles)){
  #Load and minpulate Trading History 
  OneBondActivity <- read.csv(TFileLink[g], header = TRUE, sep = ";") 
  OneBondActivity <- OneBondActivity[!(OneBondActivity$As.Of == "A"),]
  OneBondActivity <- OneBondActivity[,c(-2,-3,-7:-16)]
  OneBondActivity$Finra.Ticker <- as.character(OneBondActivity$Finra.Ticker)
  OneBondActivity$Date <- as.Date(OneBondActivity$Date, format = "%m/%d/%Y")
  OneBondActivity$Price <- as.numeric(gsub(",",".", OneBondActivity$Price))
  OneBondActivity$Quantity <- gsub("1MM.*",OneMM,OneBondActivity$Quantity)
  OneBondActivity$Quantity <- gsub("5MM.*",FiveMM,OneBondActivity$Quantity)
  OneBondActivity$Quantity <- as.numeric(OneBondActivity$Quantity)
  
  OneBondActivity <- OneBondActivity[!(OneBondActivity$Status == "Cancel"),]
  OneBondActivity <- OneBondActivity[!(OneBondActivity$Status == "Correction"),]
  
  TradingDays <- c(bizseq(from = BondDetails[(BondDetails$CUSIP == OneBondActivity$Finra.Ticker[1]),]$Issue.Date, to = BondDetails[(BondDetails$CUSIP == OneBondActivity$Finra.Ticker[1]),]$Maturity ,cal))
  TradingDays <- TradingDays[!(TradingDays > as.Date("2020-07-31"))]
  TradingDaysDF <- data.frame("Date" = TradingDays,"Status" = "NoTrade","Quantity" = 0, "Price" = 0,"Finra.Ticker" = OneBondActivity$Finra.Ticker[1])
  BondIssue <- data.frame("Date" = BondDetails[(BondDetails$CUSIP == OneBondActivity$Finra.Ticker[1]),]$Issue.Date,"Status" = "Issue","Quantity" = 1, "Price" = BondDetails[(BondDetails$CUSIP == OneBondActivity$Finra.Ticker[1]),]$Issue.Price,"Finra.Ticker" = OneBondActivity$Finra.Ticker[1])
  OneBondActivity <- rbind(BondIssue, OneBondActivity, TradingDaysDF)

  #Created average weighted daily prices
  OneBondActivity <- OneBondActivity %>%
    group_by(Date) %>%
    summarize(AveDailyPrice = weighted.mean(Price,Quantity),DailyVolumn = sum(Quantity), BondSize = BondDetails[(BondDetails$CUSIP == OneBondActivity$Finra.Ticker[1]),]$Issue.Volumn, CUSIP = OneBondActivity$Finra.Ticker[1])
  
  OneBondActivity <- OneBondActivity[order(OneBondActivity$Date),]
  
  #Give Days without a trade the daily price from the prior index period
  for (i in 1:nrow(OneBondActivity)){
    if (is.nan(OneBondActivity$AveDailyPrice[i]) == TRUE){
      OneBondActivity$AveDailyPrice[i] <- OneBondActivity$AveDailyPrice[i-1]
    }
  }
  
  ##Return Calculation and Weights
  BondReturn <- c(0)
  ReturnDate <- c(as.Date(OneBondActivity$Date[1]))
  BondWeight <- as.integer(c(0)) 
  PrincipleFactor <- 0
  x <- 1
  
  if (BondDetails[BondDetails$CUSIP == OneBondActivity$CUSIP[1],]$Principle.Reduced == " TRUE "){
    PrincipleChanges <- read.csv(paste(paste("Bond Files/Principle Change/", TradingFiles[g],sep = ""), ".csv",sep = ""), header = TRUE, sep = ";") #change 22 to i
    PrincipleChanges$ï..Date <- as.Date(PrincipleChanges$ï..Date, format = "%d.%m.%Y")
    PrincipleFactor[1] <- PrincipleChanges$Factor[1]
    for (i in 2:length(TradingDays)){
      if (PrincipleChanges$ï..Date[x] == TradingDays[i]){
        PrincipleFactor[i] <- PrincipleChanges$Factor[x]
        if (x != nrow(PrincipleChanges)){x <- x + 1}
      }else{
        PrincipleFactor[i] <- PrincipleFactor[i-1]
      }
    }
  }else {
    PrincipleFactor[1:nrow(OneBondActivity)] <- 1
  }
  
  
  for (i in 2:nrow(OneBondActivity)){
    BondReturn <- c(BondReturn, (OneBondActivity$AveDailyPrice[i]-OneBondActivity$AveDailyPrice[i-1])/OneBondActivity$AveDailyPrice[i-1])
    BondWeight <- c(BondWeight, (OneBondActivity$AveDailyPrice[i-1] * (BondDetails[BondDetails$CUSIP == OneBondActivity$CUSIP[1],]$Issue.Volumn * PrincipleFactor[i-1])))
  }
  OneBondActivity$BondReturn <- BondReturn
  OneBondActivity$BondWeight <- BondWeight
  
  #Adding the single bond to a long list
  TradingActivity <- rbind(TradingActivity, OneBondActivity)
}

TradingActivity <- TradingActivity[!(TradingActivity$Date < as.Date(StartDate)),]
TradingActivity <- TradingActivity[!(TradingActivity$Date > as.Date(EndDate)),]
TradingActivity <- TradingActivity[order(TradingActivity$Date),]
row.names(TradingActivity) <- 1:nrow(TradingActivity)


#Index and Weights 
Nweights <- TradingActivity[TradingActivity$Date == unique(TradingActivity$Date)[1],]$BondWeight / sum(TradingActivity[TradingActivity$Date == unique(TradingActivity$Date)[1],]$BondWeight) 

for (i in 2:length(unique(TradingActivity$Date))){
  UniqueDates <- unique(TradingActivity$Date)[i]
  SumWeights <- sum(TradingActivity[TradingActivity$Date == offset(UniqueDates,-1,cal),]$BondWeight) 
  Nweights <- c(Nweights, TradingActivity[TradingActivity$Date == UniqueDates,]$BondWeight / SumWeights)
}
TradingActivity$BondWeight <- Nweights

#Calculate the weighted daily returns for the index 
ReturnIndex <- TradingActivity %>%
  group_by(Date) %>%
  summarize(WeightedReturn = sum(BondReturn*BondWeight),DailyVolumn = sum(DailyVolumn), OutstandingVolumn = sum(BondSize),Price = sum(AveDailyPrice*BondWeight)-9.2411)

PriceReturn <- c(StartPrice)

#Truns the daily return calculations into an index 
for (i in 2:nrow(ReturnIndex)){
  PriceReturn <- c(PriceReturn, PriceReturn[i-1]*(1+ReturnIndex$WeightedReturn[i]))
}
ReturnIndex$PriceReturn <- PriceReturn

end_time <- Sys.time()
time_needed <- end_time - start_time 
time_needed
