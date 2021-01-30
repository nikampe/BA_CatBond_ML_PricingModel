#===========================================================================#
#                            Dummy Variables
#===========================================================================#
x <- read.csv(file = "Frontline Analysis.csv")
xx <- read.csv(file = "Akibare Analysed.csv")

write.csv(x$Date, file = "Frontline Dates.csv", row.names = FALSE)
write.csv(xx$Date, file = "Akibare Dates.csv", row.names = FALSE)
write.csv(x$Frontline, file = "Frontline Bond Returns.csv", row.names = FALSE)
write.csv(xx$Akibare, file = "Akibare Bond Returns.csv", row.names = FALSE)
write.csv(x$FIndex, file = "Frontline Index Returns.csv", row.names = FALSE)
write.csv(xx$AIndex, file = "Akibare Index Returns.csv", row.names = FALSE)


#For all analyzed events
Bond <- xts(data.frame(read.csv('Frontline Bond Returns.csv')), order.by = as.Date(read.csv('Frontline Dates.csv',header=F)$V1, format = "%Y-%m-%d"))
Index <- xts(data.frame(read.csv('Frontline Index Returns.csv')), order.by = as.Date(read.csv('Frontline Dates.csv',header=F)$V1, format = "%Y-%m-%d"))
Diff <- Bond - Index


y <- xts(ifelse(as.Date(index(Index)) %in% (as.Date('2018-10-10')), 1, 0), order.by = as.Date(index(Index))) #initiating the dummy variable

event_window <- 20

for (i in 1:(event_window-1)) {
  new_col <- xts(lag(y[ ,ncol(y)]))
  y <- cbind(y, new_col)
  colnames(y)[i] <- paste("y", i, sep = "")
}

y[is.na(y)] <- 0

#===========================================================================#
#                                 Model
#===========================================================================#

model <- lm(Diff ~ y)
yy <- summary(model)
yy
