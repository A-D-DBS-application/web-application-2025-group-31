from apscheduler.schedulers.background import BackgroundScheduler

def job_function():
    print("Job is running...")

scheduler = BackgroundScheduler()
scheduler.add_job(job_function, 'interval', seconds=10)

def start_scheduler():
    scheduler.start()