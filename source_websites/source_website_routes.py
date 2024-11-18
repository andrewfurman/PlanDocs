from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
import pytz
from source_websites.source_website_model import SourceWebsite, ScrapingCriteria
from source_websites.scrape_website import scrape_website
from source_websites.scrape_missing_data import scrape_missing_data

source_website_bp = Blueprint('source_website', __name__, 
                              template_folder='templates')

# Create engine and session
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)

@source_website_bp.route('/')
def index():
    session = Session()
    websites = session.query(SourceWebsite).order_by(SourceWebsite.id.asc()).all()
    
    # Convert UTC times to Eastern Time
    eastern = pytz.timezone('US/Eastern')
    for website in websites:
        if website.created_date:
            website.created_date = website.created_date.replace(tzinfo=pytz.UTC).astimezone(eastern)
        if website.updated_date:
            website.updated_date = website.updated_date.replace(tzinfo=pytz.UTC).astimezone(eastern)
    
    # Fetch scraping criteria
    scraping_criteria = session.query(ScrapingCriteria).all()
    
    session.close()
    return render_template('source_websites.html', websites=websites, scraping_criteria=scraping_criteria)

@source_website_bp.route('/add_url', methods=['POST'])
def add_url():
    url = request.form['url']
    session = Session()
    new_website = SourceWebsite(url=url)
    session.add(new_website)
    session.commit()
    session.close()
    return redirect(url_for('source_website.index'))

@source_website_bp.route('/delete/<int:id>', methods=['POST'])
def delete_website(id):
    session = Session()
    website = session.query(SourceWebsite).get(id)
    if website:
        session.delete(website)
        session.commit()
    session.close()
    return redirect(url_for('source_website.index'))

@source_website_bp.route('/scrape/<int:id>', methods=['POST'])
def scrape_website_route(id):
    scrape_website(id)
    return redirect(url_for('source_website.index'))

@source_website_bp.route('/add_found_urls', methods=['POST'])
def add_found_urls_route():
    from source_websites.add_found_urls import add_found_html_urls
    add_found_html_urls()
    return redirect(url_for('source_website.index'))

@source_website_bp.route('/scrape_missing_data', methods=['POST'])
def scrape_missing_data_route():
    scrape_missing_data()
    return redirect(url_for('source_website.index'))

@source_website_bp.route('/add_scraping_criteria', methods=['POST'])
def add_scraping_criteria():
    text_contains = request.form['text_contains']
    include_exclude = request.form['include_exclude']
    
    session = Session()
    new_criteria = ScrapingCriteria(text_contains=text_contains, include_exclude=include_exclude)
    session.add(new_criteria)
    session.commit()
    session.close()
    
    return redirect(url_for('source_website.index'))

@source_website_bp.route('/edit_scraping_criteria/<int:id>', methods=['GET', 'POST'])
def edit_scraping_criteria(id):
    session = Session()
    criteria = session.query(ScrapingCriteria).get(id)
    
    if request.method == 'POST':
        criteria.text_contains = request.form['text_contains']
        criteria.include_exclude = request.form['include_exclude']
        session.commit()
        session.close()
        return redirect(url_for('source_website.index'))
    
    session.close()
    return render_template('edit_scraping_criteria.html', criteria=criteria)

@source_website_bp.route('/delete_scraping_criteria/<int:id>', methods=['POST'])
def delete_scraping_criteria(id):
    session = Session()
    criteria = session.query(ScrapingCriteria).get(id)
    if criteria:
        session.delete(criteria)
        session.commit()
    session.close()
    return redirect(url_for('source_website.index'))