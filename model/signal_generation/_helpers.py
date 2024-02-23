def convert_signal_to_text(signal):
    if signal == 1:
        return "BUY"
    elif signal == -1:
        return "SELL"
    else:
        return "NEUTRAL"


strategies_defaults = {
    'MachineLearning': {"verbose": False, "models_dir": 'model/strategies/models'}
}
