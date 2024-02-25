from model.service.helpers import LOCAL_MODELS_LOCATION


def convert_signal_to_text(signal):
    if signal == 1:
        return "BUY"
    elif signal == -1:
        return "SELL"
    else:
        return "NEUTRAL"


strategies_defaults = {
    'MachineLearning': {"verbose": False, "models_dir": LOCAL_MODELS_LOCATION}
}
