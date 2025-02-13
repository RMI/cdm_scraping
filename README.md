# CDM PDD Scraper

This repository scrapes project design documents (PDD) from the Clean Development Mechanism Registry (https://cdm.unfccc.int/Projects/projsearch.html) based on project reference number. It is designed to download Brazil landfill gas capture projects to be further extracted using Gen AI for metadata such as coordinates, owner, gas capturing status, etc.

The script can be tailored to scrape all CDM PDD documents, which will be valuable to get emissions-related project metadata for waste and oil and gas sectors.

## Installation

1. Create a local copy of this repository.
2. Ensure you have Python installed on your computer.
3. Create a virtual environment:
    ```sh
    python3 -m venv venv
    ```
4. Activate the virtual environment:
    ```sh
    source venv/bin/activate
    ```
5. Install all the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

Run the `scraper.py` file to download all PDFs to the `downloads` folder:
```sh
python scraper.py