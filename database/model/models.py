import json
import sys
from datetime import datetime
from functools import reduce

try:
    from django.db import models
except Exception:
    print("Exception: Django Not Found, please install it with \"pip install django\".")
    sys.exit()


class TwitterUser(models.Model):

    id = models.TextField(primary_key=True)
    name = models.TextField()
    location = models.TextField()
    description = models.TextField()
    followers_count = models.IntegerField()
    friends_count = models.IntegerField()
    listed_count = models.IntegerField()
    created_at = models.DateTimeField()
    favourites_count = models.IntegerField()
    statuses_count = models.IntegerField()
    media_count = models.IntegerField()
    blocked_by = models.BooleanField()
    blocking = models.BooleanField()


class Tweet(models.Model):

    id = models.TextField(primary_key=True)
    created_at = models.DateTimeField()
    full_text = models.TextField()
    number_hashtags = models.IntegerField()
    hashtags = models.ManyToManyField('Hashtag')
    number_symbols = models.IntegerField()
    user_mentions = models.IntegerField()
    number_urls = models.IntegerField()
    number_media = models.IntegerField()
    user = models.ForeignKey(TwitterUser, on_delete=models.SET_NULL, null=True)
    in_reply_to_status = models.BooleanField()
    has_quoted_status = models.BooleanField()
    contributors = models.TextField(null=True)
    retweet_count = models.IntegerField()
    favourite_count = models.IntegerField()
    reply_count = models.IntegerField()
    quote_count = models.IntegerField()
    possibly_sensitive = models.BooleanField(default=False)


class Hashtag(models.Model):

    name = models.TextField(unique=True)


class LunarCrushTimeEntries(models.Model):

    id = models.IntegerField(primary_key=True)
    asset = models.ForeignKey('Asset', on_delete=models.SET_NULL, null=True)
    open_time = models.DateTimeField(null=True)
    open = models.FloatField(null=True)
    close = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    volume = models.BigIntegerField(null=True)
    market_cap = models.BigIntegerField(null=True)
    url_shares = models.IntegerField(null=True)
    unique_url_shares = models.IntegerField(null=True)
    reddit_posts = models.IntegerField(null=True)
    reddit_posts_score = models.IntegerField(null=True)
    reddit_comments = models.IntegerField(null=True)
    reddit_comments_score = models.IntegerField(null=True)
    tweets = models.IntegerField(null=True)
    tweet_spam = models.IntegerField(null=True)
    tweet_followers = models.IntegerField(null=True)
    tweet_quotes = models.IntegerField(null=True)
    tweet_retweets = models.IntegerField(null=True)
    tweet_replies = models.IntegerField(null=True)
    tweet_favorites = models.IntegerField(null=True)
    tweet_sentiment1 = models.IntegerField(null=True)
    tweet_sentiment2 = models.IntegerField(null=True)
    tweet_sentiment3 = models.IntegerField(null=True)
    tweet_sentiment4 = models.IntegerField(null=True)
    tweet_sentiment5 = models.IntegerField(null=True)
    tweet_sentiment_impact1 = models.IntegerField(null=True)
    tweet_sentiment_impact2 = models.IntegerField(null=True)
    tweet_sentiment_impact3 = models.IntegerField(null=True)
    tweet_sentiment_impact4 = models.IntegerField(null=True)
    tweet_sentiment_impact5 = models.IntegerField(null=True)
    social_score = models.BigIntegerField(null=True)
    average_sentiment = models.FloatField(null=True)
    sentiment_absolute = models.IntegerField(null=True)
    sentiment_relative = models.IntegerField(null=True)
    search_average = models.FloatField(null=True)
    news = models.IntegerField(null=True)
    medium = models.IntegerField(null=True)
    youtube = models.IntegerField(null=True)
    price_score = models.FloatField(null=True)
    social_impact_score = models.FloatField(null=True)
    correlation_rank = models.FloatField(null=True)
    galaxy_score = models.FloatField(null=True)
    volatility = models.FloatField(null=True)
    alt_rank = models.IntegerField(null=True)
    alt_rank_30d = models.IntegerField(null=True)
    market_cap_rank = models.IntegerField(null=True)
    percent_change_24h_rank = models.IntegerField(null=True)
    volume_24h_rank = models.IntegerField(null=True)
    social_volume_24h_rank = models.IntegerField(null=True)
    social_score_24h_rank = models.IntegerField(null=True)
    social_contributors = models.IntegerField(null=True)
    social_volume = models.IntegerField(null=True)
    price_btc = models.FloatField(null=True)
    social_volume_global = models.IntegerField(null=True)
    social_dominance = models.FloatField(null=True)
    market_cap_global = models.BigIntegerField(null=True)
    market_dominance = models.FloatField(null=True)
    percent_change_24h = models.FloatField(null=True)

    class Meta:
        unique_together = ("open_time", "asset")


class LunarCrushInfluencer(models.Model):

    asset = models.ForeignKey('Asset', on_delete=models.SET_NULL, null=True)
    twitter_screen_name = models.TextField(primary_key=True)
    display_name = models.TextField()
    volume = models.IntegerField()
    followers = models.IntegerField()
    following = models.IntegerField()
    engagement = models.IntegerField()
    volume_rank = models.IntegerField()
    followers_rank = models.IntegerField()
    engagement_rank = models.IntegerField()


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


class MessariAPI(models.Model):

    id = models.IntegerField(primary_key=True)
    asset = models.ForeignKey('Asset', on_delete=models.SET_NULL, null=True)
    open_time = models.DateTimeField(null=True)
    interval = models.FloatField(null=True, default=3600)
    open = models.FloatField(null=True)
    close = models.FloatField(null=True)
    high = models.FloatField(null=True)
    low = models.FloatField(null=True)
    volume = models.FloatField(null=True)
    bitwise_volume = models.FloatField(null=True)
    real_volume = models.FloatField(null=True)
    reddit_users = models.IntegerField(null=True)
    reddit_subscribers = models.IntegerField(null=True)
    average_transfer_value_usd = models.FloatField(null=True)
    flow_in_usd = models.FloatField(null=True)
    flow_out_usd = models.FloatField(null=True)
    transfers_count = models.IntegerField(null=True)
    transfers_volume = models.FloatField(null=True)
    active_addresses = models.IntegerField(null=True)
    blocks_count = models.IntegerField(null=True)
    transactions_count = models.IntegerField(null=True)
    mean_difficulty = models.FloatField(null=True)
    sharpe_30d = models.FloatField(null=True)
    sharpe_90d = models.FloatField(null=True)
    sharpe_1yr = models.FloatField(null=True)
    sharpe_3yr = models.FloatField(null=True)


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
            profitLoss=self.get_profit_loss(),
            color=self.color
        )

    class Meta:
        unique_together = ("name", "symbol", "interval", "strategy", "params", "exchange", "paper_trading")


class Position(models.Model):

    position = models.IntegerField()
    symbol = models.ForeignKey(Symbol, on_delete=models.SET_NULL, null=True)
    exchange = models.ForeignKey(Exchange, null=True, on_delete=models.SET_NULL)
    pipeline = models.ForeignKey('Pipeline', on_delete=models.CASCADE, null=True)
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
            pipelineName=self.pipeline.name,
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
            pipelineId=self.pipeline.id if self.pipeline else None,
        )
