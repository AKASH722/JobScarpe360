from sqlalchemy import UniqueConstraint

from connections import db


class NaukriJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    company = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text)
    salary = db.Column(db.Text)
    description = db.Column(db.Text)
    posted_day = db.Column(db.Text)
    tags = db.Column(db.Text)

    __table_args__ = (
        UniqueConstraint('title', 'company', 'location', name='unique_naukri_job'),
    )

    def __repr__(self):
        return f"<NaukriJob {self.id}>"


class IndeedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    company = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text)
    description = db.Column(db.Text)
    posted_day = db.Column(db.Text)

    __table_args__ = (
        UniqueConstraint('title', 'company', 'location', name='unique_indeed_job'),
    )

    def __repr__(self):
        return f"<IndeedJob {self.id}>"


class FlexJobsJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text, nullable=False)
    posted_day = db.Column(db.Text)
    remote = db.Column(db.Text)
    schedule = db.Column(db.Text)
    job_type = db.Column(db.Text)
    salary = db.Column(db.Text)
    description = db.Column(db.Text)

    __table_args__ = (
        UniqueConstraint('title', 'location', 'link', name='unique_flexjobs_job'),
    )

    def __repr__(self):
        return f"<FlexJobsJob {self.id}>"
