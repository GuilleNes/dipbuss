
country_chambers = {
    "Austria": "Austrian Embassy, Commercial Section (Advantage Austria)",
    "Belgium": "Belgian-Luxembourg Chamber of Commerce in Japan (BLCCJ)",
    "Canada": "Canadian Chamber of Commerce in Japan (CCCJ)",
    "Deutschland": "German Chamber of Commerce and Industry in Japan (AHK)",
    "Finland": "Finland Chamber of Commerce in Japan (FCCJ)",
    "France": "French Chamber of Commerce in Japan (CCIFJ)",
    "India": "Indian Chamber of Commerce in Japan (ICCJ)",
    "Ireland": "Ireland Chamber of Commerce in Japan (IJCC)",
    "Italy": "Italy Chamber of Commerce in Japan (ICCJ)",
    "Netherlands": "Netherlands Chamber of Commerce in Japan (NCCJ)",
    "Philippines": "Philippine Chamber of Commerce in Japan",
    "Spain": "Spanish Chamber of Commerce in Japan (SpCCJ)",
    "Sweden": "Sweden Chamber of Commerce in Japan (SCCJ)",
    "Switzerland": "Switzerland Chamber of Commerce in Japan (SCCIJ)",
    "UK": "British Chamber of Commerce in Japan (BCCJ)",
    "US": "American Chamber of Commerce in Japan (ACCJ)"
}


## Here we add the chambers url and country source in order to iterate on each
## We delete US and UK as we process them with Selenium later

country_url = {
    "Belgium": "https://blccj.or.jp/events/list",
    "France": "https://www.ccifj.or.jp/en/events/upcoming-events.html",
    "Deutschland": "https://japan.ahk.de/en/events/coming-events/page-{}?tx_ahkevents_list%5Bdemand%5D%5BarchiveRestriction%5D=active",  ### We need pagination in this case
    "Switzerland": "https://sccij.jp/events-future/",
    "Italy": "https://iccj.or.jp/upcoming-events/",
    "Canada": "https://www.cccj.or.jp/events",
    "Sweden": "https://www.sccj.org/events",
    "Spain": "https://spanishchamber.or.jp/upcoming-eventss/"
}

country_url_sel = {"US": "https://www.accj.or.jp/accj-events",
                   "UK": "https://bccjapan.com/events/"}


## We create a map of months in order to iterate trough them in the future

month_map = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
    'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
}