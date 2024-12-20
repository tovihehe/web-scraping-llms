# CosmoCaixa Event Scraper

This repository contains a Python-based web scraper designed to extract event details from CosmoCaixa, the science museum in Catalonia. The primary goal is to create a *synthetic dataset of current events* hosted by the museum, categorized by event type.

## Features
- **Extracts event data**: Retrieves event details such as name, description, dates, and prices from CosmoCaixa's website.
- **Supports multiple event categories**: Exhibitions, Activities, Planetarium, and Conferences.
- **Uses LLM for structured data extraction**: Leverages OpenAI models for parsing and organizing event details.
- **Outputs structured JSON data**: Saves the scraped data for further analysis or integration.
- **Combines all events into a single dataset**: Merges individual event files into a unified JSON file for easier use.

## File Overview

### Configuration and Templates
1. ```config/scraper_config.yaml```  
   Configuration file specifying the LLM model, temperature, and prompt template path.

2. ```templates/scraper_prompt.txt```
   A template used to instruct the LLM on how to extract and structure event details.

### Code Files

1. ```crawler.py```
   Retrieves URLs of event-specific pages based on categories. Although not used directly in creating the synthetic dataset, it provides a way to fetch links that provide more detailed descriptions and schedules for specific events.  

2. ```cosmocaixa_scraper.py```  
   The main scraper:
   - Utilizes BeautifulSoup and ScraperAPI to parse event pages.
   - Extracts event data using a LangChain-based pipeline with an LLM.
   - Outputs structured JSON files for each event type (activities, exhibitions, etc.).

3. ```create_merged_json.py```  
   Merges the JSON files generated by the scraper into a single ```merged_events.json``` file, adding metadata about the source of each event.

### Generated Data
- **Individual JSON files**: Each event type is stored in ```web_scraping_llms/json_events/{type}.json``` (e.g., activities.json).
- **Merged dataset**: All events combined into merged_events.json for unified access.

## Prerequisites
1. *Environment Variables*: Create a .env file with the following keys:
   ```bash
   SCRAPINGBEE_API_KEY=<Your ScrapingBee API Key>
   SCRAPER_API_KEY=<Your ScraperAPI Key>
   OPENAI_API_KEY=<Your OpenAI API Key>
   ```
2. *Python 3.8+*: Ensure Python is installed.

3. *Dependencies*: Install the required libraries:
```bash
   pip install -r requirements.txt
```
> [!NOTE]
> Ensure all required libraries are installed. 

## Usage

### Step 1: Configure the Scraper
- Update ```config/scraper_config.yaml``` to define the LLM and template settings.
- Adjust URLs or sections in ```cosmocaixa_scraper.py``` if CosmoCaixa's website structure changes.

### Step 2: Extract Event Data
Run the scraper to generate JSON files for each event type:
```bash
python cosmocaixa_scraper.py
```

### Step 3: Merge Event Files
Combine the extracted JSON files into a single dataset:
```bash
python create_merged_json.py
```
The merged data will be saved in merged_events.json.

## Output Example
A sample entry from the ```merged_events.json``` file:
```json
{
  "name": "Taller de Ciencias",
  "starting_date": "2023-11-25T10:00:00",
  "ending_date": "2023-11-25T12:00:00",
  "description": "Un taller interactivo sobre fenómenos científicos.",
  "price": 5.0,
  "type": "actividad",
  "source": "actividad"
}
```

## Improvements and Future Work
- **Error handling:** Add retries for failed requests and handle missing sections gracefully.
- **Dynamic parsing:** Automate detection of website changes to avoid manual updates to section IDs.
- **Enhanced dataset enrichment:** Fetch detailed descriptions and schedules from event-specific pages using crawler.py.
- **Additional LLM integration:** Use advanced prompt engineering for more accurate and structured data extraction.

## Contributions
Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.
