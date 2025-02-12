import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def download_pdd(reference_number, download_folder="downloads"):
    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Step 1: Open the CDM project search page
        search_url = "https://cdm.unfccc.int/Projects/projsearch.html"
        driver.get(search_url)
        time.sleep(2)

        # Step 2: Enter the reference number into the search field
        search_input = driver.find_element(By.NAME, "Ref")
        search_input.send_keys(str(reference_number))

        # Step 3: Click the "Search" button
        search_button = driver.find_element(By.NAME, "button")
        search_button.click()
        time.sleep(3)  # Allow time for the search results to load

        # Step 4: Locate the correct table containing the project details
        soup = BeautifulSoup(driver.page_source, "html.parser")
        tables = soup.find_all("table", class_="formTable")  # Find all tables with class 'formTable'
        
        project_url = None
        for table in tables:
            # Find the row containing the project details
            for row in table.find_all("tr"):
                columns = row.find_all("td")
                if len(columns) > 1:  # Ensure row has multiple columns
                    project_link = columns[1].find("a")  # Title column (2nd column)
                    if project_link and "href" in project_link.attrs:
                        project_url = project_link["href"]
                        break

        if not project_url:
            print(f"No project found for reference number {reference_number}.")
            return
        
        if not project_url.startswith("http"):
            project_url = "https://cdm.unfccc.int" + project_url  # Ensure full URL
        
        print(f"Project page found: {project_url}")

        # Step 5: Navigate to the project page
        driver.get(project_url)
        time.sleep(2)

        # Step 6: Find the first available <a> inside the project table (PDD link)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        project_table = soup.find("table", class_="formTable")  # Locate the main project table
        
        if not project_table:
            print("Could not find the project table on the project page.")
            return
        
        first_link = project_table.find("a", href=True)  # Find the first available link

        if not first_link or "href" not in first_link.attrs:
            print("PDD document link not found.")
            return
        
        pdd_url = first_link["href"]
        if not pdd_url.startswith("http"):
            pdd_url = "https://cdm.unfccc.int" + pdd_url  # Ensure full URL

        print(f"Downloading PDD from: {pdd_url}")

        # Step 7: Download the PDD PDF
        response = requests.get(pdd_url, stream=True)
        if response.status_code == 200:
            os.makedirs(download_folder, exist_ok=True)
            filename = os.path.join(download_folder, f"{reference_number}_PDD.pdf")
            with open(filename, "wb") as file:
                file.write(response.content)
            print(f"PDD downloaded successfully: {filename}")
        else:
            print("Failed to download PDD.")
    
    finally:
        driver.quit()

# Read the results.xlsx file
df = pd.read_excel("results.xlsx")

# Loop through the reference numbers in the Ref column
for reference_number in df['Ref']:
    download_pdd(reference_number)