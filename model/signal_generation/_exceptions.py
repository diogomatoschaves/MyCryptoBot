class OrderDeliveryError(Exception):
    """
    Raised when a generated signal could not be delivered to the execution
    service before its deadline. Failing the job (instead of returning an
    error result) puts it in RQ's FailedJobRegistry for inspection and
    triggers the failure callback for alerting.
    """

    def __init__(self, pipeline_id=None, signal=None):
        self.pipeline_id = pipeline_id
        self.signal = signal
        self.message = (
            f"Could not deliver signal {signal} for pipeline {pipeline_id} to the "
            f"execution service before the delivery deadline. The order was NOT placed."
        )

    def __str__(self):
        return self.message


class StaleSignal(Exception):
    """
    Raised when a signal job starts after its candle has already closed
    (queue backlog, worker outage): the next candle's job supersedes it,
    and firing the stale order could trade against the newer signal.
    """

    def __init__(self, pipeline_id=None, enqueued_at=None):
        self.pipeline_id = pipeline_id
        self.message = (
            f"Signal job for pipeline {pipeline_id} (enqueued at {enqueued_at}) "
            f"started after its candle period had elapsed - discarded without trading."
        )

    def __str__(self):
        return self.message
