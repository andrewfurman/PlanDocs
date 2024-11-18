# this scrape website python file has a single function that uses the BeautifulSoup python library in order to scrape the content from a website that is already in the database. Dysfunctional receive the ID of a website in the source websites database table, and then it will update the title column. The author column the updated date column based on when this is called, and then it will save the full text found on that website in the full tax column, it will not update the found URLs column.

from bs4 import BeautifulSoup
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from source_websites.source_website_model import SourceWebsite, ScrapingCriteria
from datetime import datetime
import urllib.parse

def extract_urls(soup, base_url, scraping_criteria):
    urls = set()
    for a_tag in soup.find_all('a', href=True):
        url = a_tag['href']
        full_url = urllib.parse.urljoin(base_url, url)
        
        # Check if the URL should be included
        should_include = False
        for criteria in scraping_criteria:
            if criteria.include_exclude == 'include':
                if criteria.text_contains.lower() in full_url.lower():
                    should_include = True
                    break
        
        # If no include criteria matched, include by default
        if not should_include and not any(c.include_exclude == 'include' for c in scraping_criteria):
            should_include = True
        
        # Check if the URL should be excluded
        if should_include:
            for criteria in scraping_criteria:
                if criteria.include_exclude == 'exclude':
                    if criteria.text_contains.lower() in full_url.lower():
                        should_include = False
                        break
        
        if should_include:
            urls.add(full_url)
    
    return list(urls)

def scrape_website(website_id):
    engine = create_engine(os.environ['DATABASE_URL'])
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        website = session.query(SourceWebsite).filter_by(id=website_id).first()
        if not website:
            print(f"Website with id {website_id} not found.")
            return

        # Fetch all scraping criteria
        scraping_criteria = session.query(ScrapingCriteria).all()

        response = requests.get(website.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        website.title = soup.title.string if soup.title else "No title found"

        author_tag = soup.find('meta', attrs={'name': 'author'})
        website.author = author_tag['content'] if author_tag else "Unknown"

        website.full_text = soup.get_text(separator=' ', strip=True)

        # Extract and store found URLs using the scraping criteria
        found_urls = extract_urls(soup, website.url, scraping_criteria)
        website.found_urls = ', '.join(found_urls)

        website.updated_date = datetime.utcnow()

        session.commit()
        print(f"Successfully updated website with id {website_id}")

    except Exception as e:
        print(f"An error occurred while scraping website with id {website_id}: {str(e)}")
        session.rollback()

    finally:
        session.close()