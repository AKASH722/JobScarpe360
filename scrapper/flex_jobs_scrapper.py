import requests
from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError

from connections import db
from model import FlexJobsJob


def get_jobs(search_query: str, location_query: str, max_jobs: int):
    search = search_query.strip().replace(' ', '%20')
    location = location_query.strip().replace(' ', '%2C%20')

    base_url: str = f'https://www.flexjobs.com/search?searchkeyword={search}'
    if location != '':
        base_url = f'{base_url}&joblocations={location}'

    job_listings = []
    page = 1
    while len(job_listings) < max_jobs:
        url = f"{base_url}&page={page}"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_='sc-jv5lm6-0')
            if not job_cards:
                break
            for job_card in job_cards:
                job_listings.append(scrape_job_info(job_card))
                if len(job_listings) >= max_jobs:
                    break
            page += 1
        else:
            print(f"Failed to fetch URL: {url}")
            break

    return job_listings


def scrape_job_info(job_listing):
    job_title_element = job_listing.find('a', class_='sc-jv5lm6-11')
    job_title = job_title_element.text.strip() if job_title_element else None

    link: str = 'https://www.flexjobs.com/' + job_title_element['href'] if job_title_element else None

    location_element = job_listing.find('span', class_='sc-jv5lm6-8')
    location = location_element.text.strip() if location_element else None

    job_age_element = job_listing.find('div', class_='sc-jv5lm6-16')
    job_age = job_age_element.text.strip() if job_age_element else None

    remote_option = job_listing.find('li', id=lambda x: x and x.startswith('remoteoption-'))
    remote = remote_option.text.strip() if remote_option else None

    job_schedule = job_listing.find('li', id=lambda x: x and x.startswith('jobschedule-'))
    schedule = job_schedule.text.strip() if job_schedule else None

    job_type = job_listing.find('li', id=lambda x: x and x.startswith('jobTypes-'))
    job_type_text = job_type.text.strip() if job_type else None

    salary_range = job_listing.find('li', id=lambda x: x and x.startswith('salartRange-'))
    salary = salary_range.text.strip() if salary_range else None

    description = job_listing.find('p', class_='sc-jv5lm6-4')
    job_description = description.text.strip() if description else None

    job = FlexJobsJob(
        title=job_title,
        location=location,
        link=link,
        posted_day=job_age,
        remote=remote,
        schedule=schedule,
        job_type=job_type_text,
        salary=salary,
        description=job_description
    )

    return job


def save_flex_jobs(search_query: str, location_query: str = '', max_jobs: int = 100):
    all_jobs = get_jobs(search_query, location_query, max_jobs)
    for job in all_jobs:
        try:
            db.session.add(job)
            db.session.commit()
        except (Exception, IntegrityError):
            db.session.rollback()
            continue
