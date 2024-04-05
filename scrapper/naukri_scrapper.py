from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from sqlalchemy.exc import IntegrityError

from connections import db
from model import NaukriJob


def get_jobs(search_query: str, max_jobs: int):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    search_url = search_query.strip().replace(' ', '-')
    search = search_query.strip().replace(' ', '%2C%20')

    job_listings = []
    page = 1
    while len(job_listings) < max_jobs:
        url = f'https://www.naukri.com/{search_url}-jobs-{page}?k={search}'
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, '.cust-job-tuple')))
            job_cards = driver.find_elements(By.CSS_SELECTOR, '.cust-job-tuple')
            if not job_cards:
                break
            for job_card in job_cards:
                job_listings.append(scrape_job_info(job_card))
                if len(job_listings) >= max_jobs:
                    break
            page += 1
        except Exception as e:
            print(f"Failed to fetch URL: {url} because {e}")
            break

    return job_listings


def scrape_job_info(job_listing):
    try:
        title = job_listing.find_element(By.CSS_SELECTOR, '.title').text
    except NoSuchElementException:
        title = None

    try:
        link = job_listing.find_element(By.CSS_SELECTOR, '.title').get_attribute('href')
    except NoSuchElementException:
        link = None

    try:
        company = job_listing.find_element(By.CSS_SELECTOR, '.comp-name').text
    except NoSuchElementException:
        company = None

    try:
        location = job_listing.find_element(By.CSS_SELECTOR, '.locWdth').text
    except NoSuchElementException:
        location = None

    try:
        experience = job_listing.find_element(By.CSS_SELECTOR, '.expwdth').text
    except NoSuchElementException:
        experience = None

    try:
        salary = job_listing.find_element(By.CSS_SELECTOR, '.sal').text
    except NoSuchElementException:
        salary = None

    try:
        description = job_listing.find_element(By.CSS_SELECTOR, '.job-desc').text
    except NoSuchElementException:
        description = None

    try:
        posted_day = job_listing.find_element(By.CSS_SELECTOR, '.job-post-day').text
    except NoSuchElementException:
        posted_day = None

    try:
        tags_element = job_listing.find_element(By.CSS_SELECTOR, '.tags-gt')
        tags = [tag.text for tag in tags_element.find_elements(By.CLASS_NAME, 'tag-li')]
    except NoSuchElementException:
        tags = None

    job = NaukriJob(
        title=title,
        company=company,
        location=location,
        link=link,
        experience=experience,
        salary=salary,
        description=description,
        posted_day=posted_day,
        tags=tags
    )

    return job


def save_naukri_jobs(search_query: str, max_jobs: int = 100):
    all_jobs = get_jobs(search_query, max_jobs)
    for job in all_jobs:
        try:
            db.session.add(job)
            db.session.commit()
        except (Exception, IntegrityError):
            db.session.rollback()
            continue
