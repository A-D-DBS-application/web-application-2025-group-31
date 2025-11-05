from apscheduler.schedulers.background import BackgroundScheduler

def job_function():
    print("Scheduled job is running...")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_function, 'interval', seconds=30)  # Adjust the interval as needed
    scheduler.start()

if __name__ == "__main__":
    start_scheduler()