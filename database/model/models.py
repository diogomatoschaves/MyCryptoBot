import sys
from database.model.helpers import STRATEGIES

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


class Pipeline(models.Model):

    STRATEGY_CHOICES = [(strategy_key, strategy_value["name"]) for strategy_key, strategy_value in STRATEGIES.items()]

    symbol = models.ForeignKey(Symbol, on_delete=models.SET_NULL, null=True)
    interval = models.TextField()
    strategy = models.TextField(choices=STRATEGY_CHOICES)
    params = models.TextField(blank=True, default="{}")
    exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=True, blank=True)

    class Meta:
        unique_together = ("symbol", "interval", "strategy", "params", "exchange")
