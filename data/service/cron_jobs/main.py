import logging
import os

from apscheduler.schedulers.blocking import BlockingScheduler

# Main cronjob function.
from data.service.cron_jobs.check_app_is_running import check_app_is_running

logging.info('Starting scheduler.')

interval_between_checks = os.getenv('SCHEDULER_INTERVAL', 3600)

# Create an instance of scheduler and add function.
scheduler = BlockingScheduler()
scheduler.add_job(check_app_is_running, "interval", seconds=interval_between_checks)

scheduler.start()
