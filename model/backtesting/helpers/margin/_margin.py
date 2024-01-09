

def get_maintenance_margin(symbol_brackets, notional_value, exchange='binance'):
    def get_maintenance_margin_binance():
        bracket = [bracket for bracket in symbol_brackets if notional_value < bracket["notionalCap"]][0]

        maintenance_rate = bracket["maintMarginRatio"]
        maintenance_amount = bracket["cum"]

        return maintenance_rate, maintenance_amount

    if exchange == 'binance':
        return get_maintenance_margin_binance()


def calculate_margin_ratio(
    leverage,
    units,
    side,
    entry_price,
    mark_price,
    maintenance_rate,
    maintenance_amount,
    exchange
):
    def calculate_margin_ratio_binance():

        initial_value = units * entry_price
        current_value = units * mark_price
        initial_margin = initial_value / leverage

        margin_balance = initial_margin + (current_value - initial_value) * side

        maintenance_margin = current_value * maintenance_rate - maintenance_amount

        return maintenance_margin / margin_balance

    if exchange == 'binance':
        return calculate_margin_ratio_binance()


def calculate_liquidation_price(
    units,
    entry_price,
    side,
    leverage,
    maintenance_rate,
    maintenance_amount,
    exchange
):
    def calculate_liquidation_ratio_binance():

        notional_value = units * entry_price
        wallet_balance = notional_value / leverage

        liquidation_price = ((wallet_balance + maintenance_amount - side * units * entry_price) /
                             (units * maintenance_rate - side * units))

        return liquidation_price

    if exchange == 'binance':
        return calculate_liquidation_ratio_binance()
