import logging

from apscheduler.schedulers.background import BackgroundScheduler

from execution.service.cron_jobs.save_pipelines_snapshot import save_portfolio_value_snapshot
from shared.utils.decorators import handle_db_connection_error
from shared.utils.settings import settings


@handle_db_connection_error
def start_background_scheduler():

    logging.info('Starting scheduler.')

    # Create an instance of scheduler and add function.
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: save_portfolio_value_snapshot(),
        "interval",
        seconds=settings.app_snapshot_interval_seconds
    )

    scheduler.start()
