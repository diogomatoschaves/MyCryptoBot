import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler

from data.service.cron_jobs.app_health import check_app_health
from shared.utils.decorators import general_app_error, handle_db_connection_error


@general_app_error
@handle_db_connection_error
def start_background_scheduler(config_vars):

    logging.info('Starting scheduler.')

    interval_between_checks = os.getenv('CHECKS_INTERVAL', config_vars.app_check_interval_seconds)

    # Create an instance of scheduler and add function.
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_app_health, "interval", seconds=int(interval_between_checks))

    scheduler.start()
