import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler

from data.service.cron_jobs.check_app_is_running import check_app_is_running


def start_background_scheduler():

    logging.info('Starting scheduler.')

    interval_between_checks = os.getenv('CHECKS_INTERVAL', 3600)

    # Create an instance of scheduler and add function.
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_app_is_running, "interval", seconds=int(interval_between_checks))

    scheduler.start()
