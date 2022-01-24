from collections import namedtuple


RESPONSES = namedtuple(
    'Responses',
    [
        "STRATEGY_INVALID",
        "SIGNAL_GENERATION_INPROGRESS",
        "NO_SUCH_PIPELINE",
        "JOB_NOT_FOUND",
        "FINISHED",
        "IN_QUEUE",
        "WAITING",
        "FAILED",
    ]
)


ReturnCodes = RESPONSES(
    STRATEGY_INVALID="STRATEGY_INVALID",
    SIGNAL_GENERATION_INPROGRESS="SIGNAL_GENERATION_INPROGRESS",
    NO_SUCH_PIPELINE="NO_SUCH_PIPELINE",
    JOB_NOT_FOUND="JOB_NOT_FOUND",
    FINISHED="FINISHED",
    IN_QUEUE="IN_QUEUE",
    WAITING="WAITING",
    FAILED="FAILED",
)


Responses = RESPONSES(
    STRATEGY_INVALID=lambda strategy: {
        "code": ReturnCodes.STRATEGY_INVALID,
        "success": False,
        "message": f"{strategy} is not a valid strategy.",
    },
    SIGNAL_GENERATION_INPROGRESS=lambda job_id: {
        "code": ReturnCodes.SIGNAL_GENERATION_INPROGRESS,
        "success": True,
        "message": f"Signal generation process started.",
        "job_id": job_id
    },
    NO_SUCH_PIPELINE=lambda pipeline_id: {
        "code": ReturnCodes.NO_SUCH_PIPELINE,
        "success": False,
        "message": f"Pipeline {pipeline_id} was not found.",
    },
    FINISHED=lambda result: {
        "code": ReturnCodes.FINISHED,
        "success": result,
        "status": 'Job finished.',
    },
    JOB_NOT_FOUND={
        "code": ReturnCodes.JOB_NOT_FOUND,
        "status": 'Job not found.'
    },
    IN_QUEUE={
        "code": ReturnCodes.IN_QUEUE,
        "status": 'Job in queue.'
    },
    WAITING={
        "code": ReturnCodes.WAITING,
        "status": 'Job waiting.'
    },
    FAILED={
        "code": ReturnCodes.FAILED,
        "status": 'Job failed.'
    },
)
