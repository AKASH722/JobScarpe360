import requests
from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError

from connections import db
from model import IndeedJob
from scrapper.util import get_dynamic_cookies

headers: dict = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}


def get_jobs(search_query: str, location_query: str, max_jobs: int):
    search = search_query.strip().replace(' ', '+').lower()
    location = location_query.strip().replace(' ', ', ').lower()

    cookies: dict = get_dynamic_cookies('https://in.indeed.com')

    base_url: str = f'https://in.indeed.com/m/jobs?q={search}'
    if location != '':
        base_url = f'{base_url}&l={location}'

    job_listings = []
    start_index = 0
    while len(job_listings) < max_jobs:
        url = f"{base_url}&start={start_index}"
        response = requests.get(url, headers=headers, cookies=cookies)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            if not job_cards:
                break
            for job_card in job_cards:
                job_listings.append(scrape_job_info(job_card))
                if len(job_listings) >= max_jobs:
                    break
            start_index += len(job_cards)
        else:
            print(f'Failed to fetch URL: {url}')
            break

    return job_listings


def scrape_job_info(job_card):
    job_title_element = job_card.find('h2', class_='jobTitle')
    job_title: str = job_title_element.text.strip() if job_title_element else None

    job_post_state_element = job_card.find('span', class_='css-92r8pb')
    company_name: str = job_post_state_element.text.strip() if job_post_state_element else None

    location_element = job_card.find('div', class_='css-1p0sjhy')
    location: str = location_element.text.strip() if location_element else None

    link_element = job_card.find('a', class_='jcs-JobTitle')
    link: str = 'https://in.indeed.com' + link_element['href'] if link_element else None

    meta_data_element = job_card.find('div', class_='jobMetaDataGroup')
    if meta_data_element:
        meta_data_items = meta_data_element.find_all('div', class_='css-1cvo3fd')
        meta_data: list = [item.text.strip() for item in meta_data_items]
    else:
        meta_data: list = []

    job_description_element = job_card.find('div', class_='css-9446fg')
    if job_description_element:
        li_elements = job_description_element.find_all('li')
        job_description: list = [li.text.strip() for li in li_elements]
    else:
        job_description: list = []

    job_post_state_element = job_card.find('span', class_='css-qvloho')
    job_post_state: str = job_post_state_element.contents[-1].text.strip() if job_post_state_element else None

    job = IndeedJob(
        title=job_title,
        company=company_name,
        location=location,
        link=link,
        tags=meta_data,
        description=job_description,
        posted_day=job_post_state
    )

    return job


def save_indeed_jobs(search_query: str, location_query: str = '', max_jobs: int = 100):
    all_jobs = get_jobs(search_query, location_query, max_jobs)
    for job in all_jobs:
        try:
            db.session.add(job)
            db.session.commit()
        except (Exception, IntegrityError):
            db.session.rollback()
            continue
