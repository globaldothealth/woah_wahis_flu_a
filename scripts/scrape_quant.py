#Code to extract quantitative data summary table from WOAH
#def for extracting data
#SV Scarpino for Globa.Health
#June 2024

#libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import json
import time

#obviously this is lazy to have it all in one long def
def scrape_QDS(EVENT, REPORT_ID):
    # Set up the Selenium web driver 
    service = Service('/usr/local/bin/chromedrive')  #using chrome
    options = webdriver.ChromeOptions()
    options.headless = True  # Run in headless mode to not open a browser window (this doesn't seem to be working)

    # Initialize the driver
    driver = webdriver.Chrome()

    #set URL
    #EVENT = '4451'
    #REPORT_ID = '167874'
    url = 'https://wahis.woah.org/#/in-review/' + EVENT + '?reportId=' + REPORT_ID
    driver.get(url)

    # Parse page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Extract the "Quantitative Data Summary" (QDS) section
    data_summary_header = soup.find(string=re.compile('QUANTITATIVE DATA SUMMARY'))
    if data_summary_header:
        data_summary_div = data_summary_header.find_parent('div')
    else:
        data_summary_div = None

    if not data_summary_div:
        print("QQUANTITATIVE DATA SUMMARY section not found.")
    else:
        data_summary = {}

    #Extract data from QDS (the table is formatted in a bespoke manner and doesn't use an html table object)
    headers = []
    row_names = []
    rows = []
    for entry in data_summary_div.find_all('mat-grid-tile'):
        style_check = entry.get('style', '')
        colspan_check = entry.get('colspan')
        rowspan_check = entry.get('rowspan')
        if 'border-bottom:' in style_check: #headers have a border-bottom
            headers.append(entry.text.strip())
        else:
            if entry.text.strip():
                if colspan_check == '1' and rowspan_check == '1':
                    rows.append(entry.text.strip())
                else:
                    if colspan_check == '2' and rowspan_check == '2': #row names have multi-row/col padding
                        row_names.append(entry.text.strip())
                    else:
                        print('Found entry with unexpected numbers for rowspan and colspan')

    #check to make sure we found the expected dimension of data
    dim_check = ((2*len(row_names))+len(rows)) / len(headers)

    assert dim_check.is_integer(), 'The length of row_names times the length of headers must be an even multiple of the number of entries in rows'
    # Print headers to debug

    #now double the length of the row names interleaving them (FIXME - Would be great to not hard code the NEW and TOTAL)
    row_names_doubled = []
    for i in row_names:
        row_names_doubled.append(i + ' - NEW')
        row_names_doubled.append(i + ' - TOTAL')

    #now build the full data set that fills in the padded row names (FIXME - Would be great to not hard code NEW and TOTAL)
    rows_fixed = []
    count = 0
    for i in rows:
        if i == 'NEW' or i == 'TOTAL':
            rows_fixed.append(row_names_doubled[count])
            rows_fixed.append(i)
            count = count + 1
        else:
            rows_fixed.append(i)

    # Now dump into dictionary
    table_dict = {}

    # Combine lists into dictionary
    for i, row in enumerate(row_names_doubled):
        row_dict = {}
        for j, col in enumerate(headers):
            row_dict[col] = rows_fixed[i * len(headers) + j]
        table_dict[row] = row_dict

    return table_dict

if __name__ == "__main__":
    import sys
    event_id = sys.argv[1]
    report_id = sys.argv[2]
    result = scrape_QDS(event_id, report_id)
    filename = 'WOAH_QDS_EVENT_' + event_id + '_REPORT ID_' + report_id + ".json" 
    with open(filename, 'w') as f:
        json.dump(result, f, indent=4)
