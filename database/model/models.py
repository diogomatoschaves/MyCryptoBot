import json
import sys
from datetime import datetime
from functools import reduce

try:
    from django.db import models
except Exception:
    print("Exception: Django Not Found, please install it with \"pip install django\".")
    sys.exit()


class Asset(models.Model):

    symbol = models.TextField(primary_key=True)
    name = models.TextField(null=True)
    slug = models.TextField(null=True)
    stats_date = models.DateTimeField(null=True)
    market_cap_ranking = models.IntegerField(null=True)

    category = models.TextField(null=True)
    sector = models.TextField(null=True)
    overview = models.TextField(null=True)
    technology = models.TextField(null=True)
    tagline = models.TextField(null=True)

    all_time_high_price = models.FloatField(null=True)
    all_time_high_date = models.DateTimeField(null=True)
    developer_activity_stars = models.IntegerField(null=True)
    developer_activity_commits_last_3_months = models.IntegerField(null=True)
    developer_activity_commits_last_1_year = models.IntegerField(null=True)
    asset_created_at = models.DateTimeField(null=True)

    token_usage = models.TextField(null=True)
    token_type = models.TextField(null=True)
    token_launch_style = models.TextField(null=True)
    token_initial_supply = models.TextField(null=True)
    token_is_treasury_decentralized = models.BooleanField(null=True)
    token_mining_algorithm = models.TextField(null=True)
    token_next_halving_date = models.TextField(null=True)
    token_emission_type_general = models.TextField(null=True)
    token_emission_type_precise = models.TextField(null=True)
    token_max_supply = models.FloatField(null=True)

    relevant_resources = models.ManyToManyField('AssetResources')


class AssetResources(models.Model):

    name = models.TextField(null=True)
    url = models.TextField(null=True)


class Symbol(models.Model):

    name = models.TextField(primary_key=True)
    base = models.ForeignKey(Asset, null=True, on_delete=models.SET_NULL, related_name='base_asset')
    quote = models.ForeignKey(Asset, null=True, on_delete=models.SET_NULL, related_name='quote_asset')


class Exchange(models.Model):

    name = models.TextField(primary_key=True)


class ExchangeData(models.Model):

    exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
    open_time = models.DateTimeField(null=True, db_index=True)
    close_time = models.DateTimeField(null=True)
    symbol = models.ForeignKey(Symbol, null=True, on_delete=models.SET_NULL)
    interval = models.TextField()
    open = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    close = models.FloatField(null=True)
    volume = models.FloatField(null=True)
    quote_volume = models.FloatField(null=True)
    trades = models.IntegerField(null=True)
    taker_buy_asset_volume = models.FloatField(null=True)
    taker_buy_quote_volume = models.FloatField(null=True)

    class Meta:
        unique_together = ("open_time", "exchange", "interval", "symbol")

    def __repr__(self):
        return self.__class__.__name__


class StructuredData(models.Model):

    open_time = models.DateTimeField(null=True, db_index=True)
    close_time = models.DateTimeField(null=True)
    exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
    symbol = models.ForeignKey(Symbol, null=True, on_delete=models.SET_NULL)
    interval = models.TextField()
    open = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    close = models.FloatField(null=True)
    volume = models.FloatField(null=True)
    quote_volume = models.FloatField(null=True)
    trades = models.IntegerField(null=True)
    taker_buy_asset_volume = models.FloatField(null=True)
    taker_buy_quote_volume = models.FloatField(null=True)

    def __repr__(self):
        return self.__class__.__name__

    class Meta:
        unique_together = ("open_time", "exchange", "interval", "symbol")


class Jobs(models.Model):

    job_id = models.TextField(null=True)
    exchange = models.ForeignKey('Exchange', on_delete=models.CASCADE)
    app = models.TextField()

    class Meta:
        unique_together = ("job_id", "exchange", "app")


class Orders(models.Model):

    order_id = models.IntegerField(primary_key=True)
    client_order_id = models.TextField(null=True)
    symbol = models.ForeignKey(Symbol, on_delete=models.SET_NULL, null=True)
    transact_time = models.DateTimeField()
    price = models.FloatField()
    original_qty = models.FloatField()
    executed_qty = models.FloatField()
    cummulative_quote_qty = models.FloatField()
    status = models.TextField()
    type = models.TextField()
    side = models.TextField()
    is_isolated = models.BooleanField(default=False)
    exchange = models.ForeignKey(Exchange, default='binance', on_delete=models.SET_DEFAULT)
    mock = models.BooleanField(null=True, default=False)
    pipeline = models.ForeignKey('Pipeline', on_delete=models.SET_NULL, null=True)


class Pipeline(models.Model):

    name = models.TextField(null=True, blank=True)
    symbol = models.ForeignKey(Symbol, on_delete=models.SET_NULL, null=True)
    interval = models.TextField()
    strategy = models.TextField()
    params = models.TextField(blank=True, default="{}")
    allocation = models.FloatField(null=True)
    exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
    paper_trading = models.BooleanField(default=False, blank=True, null=True)
    active = models.BooleanField(default=True, blank=True)
    open_time = models.DateTimeField(auto_now_add=True, null=True)

    def get_profit_loss(self):
        result = reduce(
            lambda accum, trade: [
                accum[0] + trade.profit_loss * trade.amount,
                accum[1] + trade.amount
            ] if trade.profit_loss else accum,
            self.trade_set.iterator(),
            [0, 0]
        )

        return round(result[0] / result[1] if result[1] > 0 else 0, 5)

    def as_json(self):
        return dict(
            name=self.name,
            id=self.id,
            strategy=self.strategy,
            params=json.loads(self.params),
            allocation=self.allocation,
            candleSize=self.interval,
            exchange=self.exchange.name,
            symbol=self.symbol.name,
            active=self.active,
            paperTrading=self.paper_trading,
            openTime=self.open_time.isoformat() if self.open_time else None,
            numberTrades=self.trade_set.count(),
            profitLoss=self.get_profit_loss()
        )

    class Meta:
        unique_together = ("name", "symbol", "interval", "strategy", "params", "exchange", "paper_trading")


class Position(models.Model):

    position = models.IntegerField()
    symbol = models.ForeignKey(Symbol, on_delete=models.SET_NULL, null=True)
    exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
    pipeline = models.ForeignKey('Pipeline', on_delete=models.SET_NULL, null=True)
    paper_trading = models.BooleanField(default=False, blank=True, null=True)
    buying_price = models.FloatField()
    amount = models.FloatField()
    open = models.BooleanField(default=True, blank=True)
    open_time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(null=True, blank=True)

    def as_json(self):
        return dict(
            id=self.id,
            position=self.position,
            symbol=self.symbol.name,
            exchange=self.exchange.name,
            pipelineId=self.pipeline.id,
            paperTrading=self.paper_trading,
            price=self.buying_price,
            amount=self.amount,
            open=self.open,
            openTime=self.open_time,
            closeTime=self.close_time
        )


class Trade(models.Model):

    symbol = models.ForeignKey(Symbol, on_delete=models.SET_NULL, null=True)
    open_time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(null=True, blank=True)
    open_price = models.FloatField()
    close_price = models.FloatField(null=True, blank=True)
    amount = models.FloatField()
    profit_loss = models.FloatField(null=True, blank=True)
    side = models.IntegerField()
    exchange = models.ForeignKey(Exchange, default='binance', on_delete=models.SET_DEFAULT)
    mock = models.BooleanField(null=True, default=False)
    pipeline = models.ForeignKey('Pipeline', on_delete=models.SET_NULL, null=True)

    def as_json(self):
        return dict(
            id=self.id,
            symbol=self.symbol.name,
            exchange=self.exchange.name,
            openTime=self.open_time,
            closeTime=self.close_time,
            openPrice=self.open_price,
            closePrice=self.close_price,
            profitLoss=self.profit_loss,
            amount=self.amount,
            side=self.side,
            mock=self.mock,
            pipeline_id=self.pipeline.id,
        )
