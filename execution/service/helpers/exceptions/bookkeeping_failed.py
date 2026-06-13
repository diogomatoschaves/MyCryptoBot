class BookkeepingFailed(Exception):
    """
    Raised when the exchange accepted an order but the local bookkeeping
    (Orders/Trade/Position/pipeline state) could not be committed. The
    pipeline must be frozen: every later computation would start from
    stale local state. Startup reconciliation repairs the records.
    """

    def __init__(self, pipeline_id=None, detail=None):
        self.pipeline_id = pipeline_id
        self.message = (
            f"Bookkeeping failed after the exchange was updated "
            f"(pipeline {pipeline_id}){': ' + str(detail) if detail else ''}. "
            f"Pipeline deactivated; records will be reconciled at next startup."
        )

    def __str__(self):
        return f"{self.message}"

    def __repr__(self):
        return self.__class__.__name__
