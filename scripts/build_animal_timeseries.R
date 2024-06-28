#Converting WOAH report data into a time series
#SV Scarpino for Global.health
#June 2024

###########
#libraries#
###########
library(jsonlite)

###########
#Acc Funcs#
###########
data_frame_colname_set <- function(x){
  datdf_raw <- as.data.frame(x)
  colnames(datdf_raw)[2] <- "NEW_or_TOTAL"
  return(datdf_raw)
}

load_json_to_df <- function(filename){
  dat_raw <- read_json(path = filename)
  dat_flatten <- as.data.frame(do.call(rbind, lapply(dat_raw, data_frame_colname_set)))
  return(dat_flatten)
}

get_report_id <- function(filename){
  split_id <- strsplit(x = filename, split = "REPORT ID_")[[1]][2]
  split_id_2 <- strsplit(x = split_id, split = ".json")[[1]][1]
  return(split_id_2)
}

rep_dash_zero <- function(x){
  for(i in 1:ncol(x)){
    rep.i <- which(x[,i] == "-")
    if(length(rep.i) > 0){
      x[rep.i,i] <- 0
      x[,i] <- as.numeric(x[,i])
    }
  }
  return(x)
}
#########
#Globals#
#########
timestamp <- as.numeric(Sys.time())
save_file <- FALSE

######
#Data#
######
meta <- read.csv("../data/Event 4451/HistoricalReport.csv")

json_location <- list.files('../data/Event 4451/QDS', full.names = TRUE)

######################
#Building time series#
######################
use_cols <- c("Species", "Susceptible", "Cases", "Deaths", "Killed.and.Disposed.of", "Slaughtered..Killed.for.commercial.use", "Vaccinated")

mat_full <- matrix(NA, nrow = 1, ncol = length(use_cols))
colnames(mat_full) <- use_cols
dat_full <- as.data.frame(mat_full)
Report_Date <- c()
Report_ID <- c()
Event_ID <- c()

for(f in json_location){
  #getting report date
  id.f <- get_report_id(filename = f)
  
  use.f <- which(meta$reportId == id.f)
  
  if(length(use.f) != 1){
    stop("Did not find a single match on report ID")
  }
  
  date.f <- meta$reportingDate[use.f]
  
  #loading and organizing report data
  dat.f <- load_json_to_df(filename = f)
  
  use.rows <- which(dat.f$NEW_or_TOTAL == "NEW")
  
  dat.keep.f <- dat.f[use.rows, use_cols]
  
  dat.keep.num.f <- rep_dash_zero(dat.keep.f)
  
  #storing results
  Report_Date <- c(Report_Date, rep(date.f, nrow(dat.keep.num.f)))
  Report_ID <- c(Report_ID, rep(id.f, nrow(dat.keep.num.f)))
  Event_ID <- c(Event_ID, rep("4451", nrow(dat.keep.num.f)))
  dat_full <- rbind(dat_full, dat.keep.num.f)
}
#creating a col for wild/dom
Wild_or_Domestic <- rep(NA, nrow(dat_full))
Wild_or_Domestic[grep(pattern = "(WILD)", x = dat_full$Species)] <- "Wild"
Wild_or_Domestic[grep(pattern = "(DOMESTIC)", x = dat_full$Species)] <- "Domestic"
Wild_or_Domestic <- Wild_or_Domestic[-1]

#combining results
dat_out <- data.frame(Event_ID,  Report_ID, Report_Date, Wild_or_Domestic, dat_full[-1,])

#std. date
dat_out$Report_Date <- as.Date(strptime(dat_out$Report_Date, format = "%m/%d/%Y"))

#removing "-NEW"
dat_out$Species <- gsub(pattern = " - NEW", replacement = "", x = dat_out$Species)

#removing "all_species"
rm_all <- which(dat_out$Species == "All species")
if(length(rm_all) > 0){
  dat_out <- dat_out[-rm_all, ]
}

#removing (WILD) and (DOMESTIC)
dat_out$Species <- gsub(pattern = " (DOMESTIC)", fixed = TRUE, replacement = "", x = dat_out$Species)
dat_out$Species <- gsub(pattern = " (WILD)", fixed = TRUE, replacement = "", x = dat_out$Species)

#saving file
if(save_file == TRUE){
  filename <- paste0("output/", timestamp, "_EVENTID_4451_Epilist.csv")
  write.csv(x = dat_out, file = filename, row.names = FALSE)
}
