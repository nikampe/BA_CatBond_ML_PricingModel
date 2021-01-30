#Bond Price Return

#What I need 
#change in spreads 
#coupon payment dates


PriceIndex2 <- PriceIndex[!(PriceIndex$Date < as.Date("2015-12-31")),] #Alles ab 2016

for (i in 3:nrow(PriceIndex2)){
  if (PriceIndex2$DailyVolumn[i] == 1){
    PriceIndex2$DailyVolumn[i] <- PriceIndex2$DailyVolumn[i-1]
  }
}
PriceIndex2 <- PriceIndex2[-1:-2,]

returndate <- as.Date(c(PriceIndex2$Date[1]))
returnp <- as.double(c(0.0)) 

for (i in 2:nrow(PriceIndex2)){
  r <- weighted.mean(c(PriceIndex2$AveDailyPrice[i],PriceIndex2$AveDailyPrice[i-1]),c(PriceIndex2$DailyVolumn[i],PriceIndex2$DailyVolumn[i-1]))
  r <- ((PriceIndex2$AveDailyPrice[i]*PriceIndex2$DailyVolumn[i])-(PriceIndex2$AveDailyPrice[i-1])*PriceIndex2$DailyVolumn[i-1])/(PriceIndex2$AveDailyPrice[i-1]*PriceIndex2$DailyVolumn[i-1])
  returnp <- c(returnp, r)
  returndate <- c(returndate, PriceIndex2$Date[i])
}
ReturnIndex <- data.frame(returnp, returndate)

ggplot(data = ReturnIndex, aes(x= returndate)) + geom_line(aes(y= returnp)) + scale_y_continuous(labels = comma)


x <- as.double(c(100.00))
y <- as.Date(c(ReturnIndex$returndate[1]-1))

for (i in 1:nrow(ReturnIndex)){
  x <- c(x, (x[i]*(1+ReturnIndex$returnp[i])))
  y <- c(y, ReturnIndex$returndate[i])
}
Index <- data.frame(x,y)

ggplot(data = Index, aes(x= y)) + geom_line(aes(y= x))


month(ReturnIndex$returndate[1])

#Bonds of the same firms 
#multi spead


######################################################################
# To Do
# EVent Study code
#check specfic event and the returns / price moves
# Get the Swiss Re Indices to check whether price return is enough
# spreads for the indivifual bonds 
# aggregate bonds on price or return level?
######################################################################
#On a Bonds basse
#Price calculation - average per day
#keep the "current" price of the bond rolling
#average the return caluation with the size of the bond 
