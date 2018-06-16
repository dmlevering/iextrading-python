from enum import Enum

class Constants(object):
    class DataType(Enum):
        BATCH            = "batch"
        BOOK             = "book"
        CHART            = "chart"
        COMPANY          = "company"
        DELAYED_QUOTE    = "delayed-quote"
        DIVIDENDS        = "dividends"
        EARNINGS         = "earnings"
        EFFECTIVE_SPREAD = "effective-spread"
        FINANCIALS       = "financials"
        GAINERS          = "gainers"
        KEY_STATS        = "stats"
        LARGEST_TRADES   = "largest-trades"
        LIST             = "list"
        LOGO             = "logo"
        LOSERS           = "losers"
        MARKET           = "market"
        MOST_ACTIVE      = "mostactive"
        NEWS             = "news"
        PRICE            = "price"
        QUOTE            = "quote"
        STOCK            = "stock"
        TIME_SERIES      = "time-series"

    class DataRange(Enum):
        FIVE_YEARS   = "5y"      #historically adjusted market-wide data
        TWO_YEARS    = "2y"      #^
        YEAR_TO_DATE = "ytd"     #^
        SIX_MONTHS   = "6m"      #^
        THREE_MONTHS = "3m"      #^
        ONE_MONTH    = "1m"      #^
        ONE_DAY      = "1d"      #IEX-only data by minute
        DATE         = "date"    #IEX-only data by minute for a specified date
                                 #in the format YYYYMMDD (e.g., /date/19970408)
        DYNAMIC      = "dynamic" #returns 1d or 1m data depending on the day
                                 #or week and time of day. Intraday per minute
                                 #data is only returned during market hours.
