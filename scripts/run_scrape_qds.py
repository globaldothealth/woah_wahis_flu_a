#Code to extract quantitative data summary table from WOAH
#Iterate over report IDs
#SV Scarpino for Globa.Health
#June 2024

#libraries
import pandas as pd
import json
from scrape_quant import scrape_QDS

# Iterate over the event_ids and call scrape_QDS
event_id = '4451'

# Load the report IDS from a CSV file
csv_file = 'HistoricalReport.csv'  # Replace with the path to your CSV file
csv_file_path = '../data/Event ' + event_id + "/"

df = pd.read_csv(csv_file_path + csv_file)

for report_id_int in df['reportId']:
    report_id = str(report_id_int)
    try:
        # Call the scrap_event function
        dict_result = scrape_QDS(event_id, report_id)
        #save the dict as JSON
        filename = 'WOAH_QDS_EVENT_' + event_id + '_REPORT ID_' + report_id + ".json" 
        with open('output/' + filename, 'w') as f:
            json.dump(dict_result, f, indent=4)
    except Exception as e:
        print(f"Error processing event_id {event_id}: {e}")
