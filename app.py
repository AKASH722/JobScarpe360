from sqlalchemy import or_

from flask import request, jsonify, render_template

from connections import app, db
from model import NaukriJob, IndeedJob, FlexJobsJob
from scrapper.flex_jobs_scrapper import save_flex_jobs
from scrapper.indeed_scrapper import save_indeed_jobs
from scrapper.naukri_scrapper import save_naukri_jobs


@app.route('/scrape-jobs', methods=['POST'])
def scrape_jobs():
    data = request.get_json()
    search_query = data.get('search_query')
    location_query = data.get('location_query')
    save_flex_jobs(search_query, location_query, 50)
    save_indeed_jobs(search_query, location_query, 50)
    save_naukri_jobs(search_query, 50)

    naukri_jobs_to_delete = NaukriJob.query.filter(NaukriJob.posted_day.ilike('%30%')).all()
    for job in naukri_jobs_to_delete:
        db.session.delete(job)
    indeed_jobs_to_delete = IndeedJob.query.filter(IndeedJob.posted_day.ilike('%30%')).all()
    for job in indeed_jobs_to_delete:
        db.session.delete(job)
    flexjobs_jobs_to_delete = FlexJobsJob.query.filter(FlexJobsJob.posted_day.ilike('%30%')).all()
    for job in flexjobs_jobs_to_delete:
        db.session.delete(job)
    db.session.commit()
    return jsonify('scrapped')


@app.route('/search-jobs', methods=['POST'])
def search_jobs():
    search_query = request.json.get('search_query')
    location_query = request.json.get('location_query')

    # Split search_query by space
    search_terms = search_query.split()

    # Create an empty list to store search results
    naukri_jobs = []
    indeed_jobs = []
    flex_jobs = []

    # Query each job table for each search term and combine the results
    for term in search_terms:
        naukri_jobs += NaukriJob.query.filter(or_(
            NaukriJob.title.ilike(f'%{term}%'),
            NaukriJob.location.ilike(f'%{term}%'),
            NaukriJob.description.ilike(f'%{term}%')
        )).all()

        indeed_jobs += IndeedJob.query.filter(or_(
            IndeedJob.title.ilike(f'%{term}%'),
            IndeedJob.location.ilike(f'%{term}%'),
            IndeedJob.description.ilike(f'%{term}%')
        )).all()

        flex_jobs += FlexJobsJob.query.filter(or_(
            FlexJobsJob.title.ilike(f'%{term}%'),
            FlexJobsJob.location.ilike(f'%{term}%'),
            FlexJobsJob.description.ilike(f'%{term}%')
        )).all()

    return render_template('index.html', naukri_jobs=naukri_jobs, indeed_jobs=indeed_jobs, flex_jobs=flex_jobs)


@app.route('/')
def index():
    naukri_jobs = NaukriJob.query.all()
    indeed_jobs = IndeedJob.query.all()
    flex_jobs = FlexJobsJob.query.all()

    return render_template('index.html', naukri_jobs=naukri_jobs, indeed_jobs=indeed_jobs, flex_jobs=flex_jobs)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
