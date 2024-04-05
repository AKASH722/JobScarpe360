import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_dynamic_cookies(url: str):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    cookies = driver.get_cookies()
    driver.quit()
    cookies_dict: dict = {cookie['name']: cookie['value'] for cookie in cookies}
    return cookies_dict


def save_jobs_to_csv(jobs: list, fieldnames: list, filename: str = 'jobs.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            writer.writerow(job)
