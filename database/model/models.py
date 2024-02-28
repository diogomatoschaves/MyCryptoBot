import json
import sys
import math

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


try:
    from django.db import models
except Exception:
    print("Exception: Django Not Found, please install it with \"pip install django\".")
    sys.exit()


strategy_combination_methods = ["Unanimous", "Majority"]


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


class Strategy(models.Model):
    name = models.TextField()
    params = models.TextField(blank=True, default="{}")

    def as_json(self):
        return dict(
            name=self.name,
            params=json.loads(self.params),
        )

    def __str__(self):
        return self.name


class Pipeline(models.Model):

    name = models.TextField(null=True, blank=True)
    symbol = models.ForeignKey(Symbol, on_delete=models.SET_NULL, null=True)
    interval = models.TextField()
    strategy = models.ManyToManyField(Strategy)
    strategy_combination = models.TextField(
        choices=((method, method) for method in strategy_combination_methods),
        default='Majority'
    )
    initial_equity = models.FloatField(null=True)
    current_equity = models.FloatField(null=True)
    exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
    paper_trading = models.BooleanField(default=False, blank=True, null=True)
    active = models.BooleanField(default=True, blank=True)
    open_time = models.DateTimeField(auto_now_add=True, null=True)
    color = models.TextField()
    leverage = models.IntegerField(blank=True, default=1)
    deleted = models.BooleanField(default=False, blank=True)
    balance = models.FloatField(null=True, blank=True)
    units = models.FloatField(default=0, blank=True)
    last_entry = models.DateTimeField(null=True, default=None)

    def as_json(self):
        return dict(
            name=self.name,
            id=self.id,
            strategy=[obj.as_json() for obj in self.strategy.all()],
            strategyCombination=self.strategy_combination,
            initialEquity=self.initial_equity,
            currentEquity=self.current_equity,
            candleSize=self.interval,
            exchange=self.exchange.name,
            symbol=self.symbol.name,
            active=self.active,
            paperTrading=self.paper_trading,
            openTime=self.open_time.isoformat() if self.open_time else None,
            numberTrades=self.trade_set.count(),
            color=self.color,
            leverage=self.leverage,
            balance=self.balance,
            units=self.units
        )

    def save(self, *args, **kwargs):
        if self.balance is None:
            self.balance = self.initial_equity * self.leverage

        if self.current_equity is None:
            self.current_equity = self.initial_equity

        super().save(*args, **kwargs)


class Position(models.Model):

    position = models.IntegerField()
    pipeline = models.ForeignKey('Pipeline', on_delete=models.CASCADE)
    buying_price = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    open_time = models.DateTimeField(auto_now_add=True, null=True)
    close_time = models.DateTimeField(null=True, blank=True)

    def as_json(self):
        return dict(
            id=self.id,
            position=self.position,
            symbol=self.pipeline.symbol.name,
            exchange=self.pipeline.exchange.name,
            pipelineId=self.pipeline.id,
            pipelineName=self.pipeline.name,
            paperTrading=self.pipeline.paper_trading,
            price=self.buying_price,
            amount=self.amount,
            openTime=self.open_time,
            closeTime=self.close_time,
            leverage=self.pipeline.leverage,
        )


class Trade(models.Model):

    pipeline = models.ForeignKey('Pipeline', on_delete=models.CASCADE)
    open_time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(null=True, blank=True)
    open_price = models.FloatField()
    close_price = models.FloatField(null=True, blank=True)
    amount = models.FloatField()
    pnl = models.FloatField(null=True, blank=True)
    pnl_pct = models.FloatField(null=True, blank=True)
    side = models.IntegerField()

    @property
    def symbol(self):
        return self.pipeline.symbol

    def get_profit_loss(self):
        return (self.close_price - self.open_price) * self.amount * self.side

    def get_profit_loss_pct(self):
        return (math.exp(math.log(self.close_price / self.open_price) * self.side) - 1) * self.pipeline.leverage

    def as_json(self):
        return dict(
            id=self.id,
            symbol=self.pipeline.symbol.name,
            exchange=self.pipeline.exchange.name,
            openTime=self.open_time,
            closeTime=self.close_time,
            openPrice=self.open_price,
            closePrice=self.close_price,
            profitLoss=self.pnl,
            profitLossPct=self.pnl_pct,
            amount=self.amount,
            side=self.side,
            mock=self.pipeline.paper_trading,
            pipelineId=self.pipeline.id,
            pipelineName=self.pipeline.name,
            pipelineColor=self.pipeline.color,
            leverage=self.pipeline.leverage,
        )


class PortfolioTimeSeries(models.Model):

    pipeline = models.ForeignKey(Pipeline, on_delete=models.SET_NULL, null=True)
    time = models.DateTimeField()
    value = models.FloatField()
    type = models.TextField(null=True, blank=True, default=None)
