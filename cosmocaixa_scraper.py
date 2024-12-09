from pydantic import BaseModel, Field
from typing import Optional
from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime, date
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from typing import List, Optional
from urllib.parse import urlencode
import concurrent.futures
import yaml

# Define a global class Event.
class Event(BaseModel):
    name: str = Field(description="El nombre del evento.")
    starting_date: Optional[datetime] = Field(description="La fecha de inicio del evento.")
    ending_date: Optional[datetime] = Field(description="La fecha de finalización del evento.")
    description: str = Field(description="La descripción del evento e detalles.")
    price: Optional[float] = Field(description="El precio del evento. Si es gratuito o no hay precio, el valor es 0.")
    type: str = Field(description="El tipo de evento. Pueden ser Exposiciones, Actividades, Planetario u Conferencias. Si son Actividades, pueden ser Talleres, Visitas guiadas, Espectáculos, Muestra u Otros.")

# Define the EventScrapper class to store the list of events.
class EventScrapper(BaseModel):
    Events: List[Event] = Field("Lista de todos los eventos listados en el texto")

# Define the EventEncoder class to encode the Event objects to JSON.
class EventEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Event):
            return {
                "name": obj.name,
                "starting_date": obj.starting_date.isoformat() if obj.starting_date else None,
                "ending_date": obj.ending_date.isoformat() if obj.ending_date else None,
                "description": obj.description,
                "price": obj.price,
                "type": obj.type
            }
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
    
# Define the ScraperConfig class to store the configuration of the scraper.
class ScraperConfig(BaseModel):
    llm_name: str = Field("gpt-3.5-turbo", description="The model to use for the scraper.")
    llm_temperature: float = Field(0.0, description="The temperature to use for the scraper.")
    template_path: str = Field("templates/scraper_template.txt", description="The path to the scraper prompt template file.")

# Define the CosmoCaixaScaper class to scrape the events
class CosmoCaixaScaper:  
    def __init__(self, config: ScraperConfig):
        self.api_key = os.getenv('SCRAPER_API_KEY')
        self.llm = ChatOpenAI(temperature=config.llm_temperature, model=config.llm_name)
        self.output_parser = PydanticOutputParser(pydantic_object=EventScrapper)

        with open(config.template_path, "r", encoding='utf-8') as file:
            self.prompt_template = file.read()
        
        self.prompt_template = PromptTemplate(
            template=self.prompt_template,
            input_variables=["html_text"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions}
        )

        self.chain = self.prompt_template | self.llm | self.output_parser

    # Define the start_requests method to start the scraping process.
    def start_requests(self):
        sources = {
            "exposiciones": ["https://cosmocaixa.org/es/exposiciones-ciencia-barcelona", "portlet_listactivities_INSTANCE_u3YZVHkpD017"],
            "actividades": ["https://cosmocaixa.org/es/actividades-cosmocaixa-ciencia", "portlet_listactivities_INSTANCE_Q4EA43110XIZ"],
            "planetario": ["https://cosmocaixa.org/es/planetario", "portlet_listactivities_INSTANCE_n4imOHR5Ia1i"],
            "conferencias": ["https://cosmocaixa.org/es/conferencias", "portlet_listactivities_INSTANCE_WvGPDs7XuZX8"]
        }
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self.parse_wrapper, sources.items())

    # Define the parse_wrapper method to parse the sources where we extract the events.
    def parse_wrapper(self, item):
        type, source = item
        url, section_id = source
        self.parse(url, type, section_id)

    # Define the parse method to parse the HTML content and extract the events.
    def parse(self, url, type, section_id):
        payload = {'api_key': self.api_key, 'url': url}
        response = requests.get('http://api.scraperapi.com/', params=urlencode(payload))

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            specific_section = soup.select_one(f'#{section_id}')
            
            if specific_section:
                result = self.chain.invoke({"html_text": str(specific_section)})
                events = result.Events
                
                with open(f'web_scraping_llms/json_events/{type}.json', 'w') as f:
                    json.dump(events, f, cls=EventEncoder)
                
                print(f"Events saved for {type}: {events}")
            else:
                print(f"Section not found for {type}")
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")

# Define the load_agent_config function to load the scraper configuration from a YAML file.
def load_agent_config(config_path: str) -> ScraperConfig:
    """Loads the agent configuration from a YAML file."""
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    return ScraperConfig(**config_data)

if __name__ == "__main__":
    # Load env 
    load_dotenv('.env', override=True)
    # Load the scraper configuration
    config = load_agent_config('config/scraper_config.yaml')
    # Define the scraper object
    scraper = CosmoCaixaScaper(config)
    # Start the scraping process
    scraper.start_requests()