import json
import sys
from functools import reduce
import math

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

try:
    from django.db import models
except Exception:
    print("Exception: Django Not Found, please install it with \"pip install django\".")
    sys.exit()


class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        """
        Creates and saves a User with the given username and password.
        """
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            username,
            password=password,
        )
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.TextField(
        verbose_name='username',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    admin = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.admin


class Asset(models.Model):

    symbol = models.TextField(primary_key=True)
    name = models.TextField(null=True)
    slug = models.TextField(null=True)
    category = models.TextField(null=True)
    sector = models.TextField(null=True)


class Symbol(models.Model):

    name = models.TextField(primary_key=True)
    base = models.ForeignKey(Asset, null=True, on_delete=models.SET_NULL, related_name='base_asset')
    quote = models.ForeignKey(Asset, null=True, on_delete=models.SET_NULL, related_name='quote_asset')
    price_precision = models.IntegerField()
    quantity_precision = models.IntegerField()


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

    order_id = models.TextField(primary_key=True)
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
    color = models.TextField()
    leverage = models.IntegerField(blank=True, default=1)
    deleted = models.BooleanField(default=False, blank=True)
    balance = models.FloatField(default=0, blank=True)
    units = models.FloatField(default=0, blank=True)
    last_entry = models.DateTimeField(null=True, default=None)

    def get_profit_loss(self):
        result = reduce(
            lambda accum, trade: [
                accum[0] + trade.profit_loss * trade.amount * (trade.leverage if trade.leverage else self.leverage),
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
            # profitLoss=self.get_profit_loss(),
            color=self.color,
            leverage=self.leverage,
            balance=self.balance,
            units=self.units
        )

    class Meta:
        unique_together = ("name", "symbol", "interval", "strategy", "params", "exchange", "paper_trading", "leverage")


class Position(models.Model):

    position = models.IntegerField()
    symbol = models.ForeignKey(Symbol, on_delete=models.SET_NULL, null=True)
    exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
    pipeline = models.ForeignKey('Pipeline', on_delete=models.CASCADE, null=True)
    paper_trading = models.BooleanField(default=False, blank=True, null=True)
    buying_price = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    open = models.BooleanField(default=True, blank=True)
    open_time = models.DateTimeField(auto_now_add=True, null=True)
    close_time = models.DateTimeField(null=True, blank=True)

    def as_json(self):
        return dict(
            id=self.id,
            position=self.position,
            symbol=self.symbol.name,
            exchange=self.exchange.name,
            pipelineId=self.pipeline.id,
            pipelineName=self.pipeline.name,
            paperTrading=self.paper_trading,
            price=self.buying_price,
            amount=self.amount,
            open=self.open,
            openTime=self.open_time,
            closeTime=self.close_time,
            leverage=self.pipeline.leverage if self.pipeline else None,
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
    leverage = models.IntegerField(null=True, default=None)

    def get_profit_loss(self):
        return math.exp(math.log(self.close_price / self.open_price) * self.side) - 1

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
            pipelineId=self.pipeline.id if self.pipeline else None,
            pipelineName=self.pipeline.name if self.pipeline else None,
            pipelineColor=self.pipeline.color if self.pipeline else None,
            leverage=self.leverage if self.leverage else self.pipeline.leverage if self.pipeline else None,
        )


class PortfolioTimeSeries(models.Model):

    pipeline = models.ForeignKey(Pipeline, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField()
    value = models.FloatField()
    type = models.TextField(null=True, blank=True, default=None)
