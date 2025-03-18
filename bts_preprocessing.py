from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import zipfile
import shutil

url = "https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr"
download_path = os.path.abspath("./bts_data")

chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

years = ["2022", "2023", "2024"]
months_2022 = ["November", "December"]
months_2024 = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November"]
months_2023 = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

for year in years:
    if year == "2024":
        months = months_2024
    elif year == "2023":
        months = months_2023
    else:
        months = months_2022

    for month in months:
        year_dropdown = Select(driver.find_element(By.ID, "cboYear"))
        geo_dropdown = Select(driver.find_element(By.ID, "cboGeography"))
        month_dropdown = Select(driver.find_element(By.ID, "cboPeriod"))

        year_dropdown.select_by_visible_text(year)
        geo_dropdown.select_by_visible_text("Massachusetts")
        month_dropdown.select_by_visible_text(month)

        field_ids = [
            # time period
            "YEAR", "MONTH", "DAY_OF_MONTH", "DAY_OF_WEEK", "FL_DATE",
            # airline
            "OP_UNIQUE_CARRIER", "OP_CARRIER_AIRLINE_ID", 
            # origin
            "ORIGIN_AIRPORT_ID", "ORIGIN_CITY_MARKET_ID", "ORIGIN", "ORIGIN_CITY_NAME",
            # destination
            "DEST_AIRPORT_ID", "DEST_CITY_MARKET_ID", "DEST", "DEST_CITY_NAME",
            # departure/arrival performance
            "DEP_DELAY", "DEP_DEL15", "ARR_DELAY", "ARR_DEL15",
            # cancellations/diversions
            "CANCELLED", "CANCELLATION_CODE", "DIVERTED",
            # flight summary
            "ACTUAL_ELAPSED_TIME", "DISTANCE",
            # cause of delay
            "CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"
        ]

        for field_id in field_ids:
            try:
                checkbox = driver.find_element(By.ID, field_id)
                if not checkbox.is_selected():
                    checkbox.click()
            except:
                print(f"Field {field_id} not found")

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnDownload")))
        
        print(f"Downloading {year} {month}")
        download_button = driver.find_element(By.ID, "btnDownload")
        download_button.click()

        # Wait for download to finish
        time.sleep(10)
        print(f"Downloaded {year} {month}")

        # Extract the ZIP file

        for filename in os.listdir(download_path):
            if filename.endswith(".zip"):
                zip_path = os.path.join(download_path, filename)
                print(f"Extracting {zip_path}")

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    temp_extracted_path = os.path.join(download_path, "temp_extract")
                    if not os.path.exists(temp_extracted_path):
                        os.makedirs(temp_extracted_path)
                    zip_ref.extractall(temp_extracted_path)

                for extracted_file in os.listdir(temp_extracted_path):
                    if extracted_file == "T_ONTIME_REPORTING.csv":
                        new_csv_filename = f"BTS_OnTime_{year}_{month}.csv"
                        new_csv_filepath = os.path.join(download_path, new_csv_filename) 
                        shutil.move(os.path.join(temp_extracted_path, extracted_file), new_csv_filepath)
                        print(f"extracted and renamed file: {new_csv_filename}")

                os.remove(zip_path) 
                shutil.rmtree(temp_extracted_path)

# Close the browser
driver.quit()