import sys

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
    token_is_treasury_decentralized = models.NullBooleanField(null=True)
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

    id = models.IntegerField(primary_key=True)
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

    # 'url_shares',
    # 'unique_url_shares', 'reddit_posts', 'reddit_posts_score',
    # 'reddit_comments', 'reddit_comments_score', 'tweets', 'tweet_spam',
    # 'tweet_followers', 'tweet_quotes', 'tweet_retweets', 'tweet_favorites',
    # 'tweet_sentiment1', 'tweet_sentiment2', 'tweet_sentiment3',
    # 'tweet_sentiment4', 'tweet_sentiment5', 'tweet_sentiment_impact1',
    # 'tweet_sentiment_impact2', 'tweet_sentiment_impact3',
    # 'tweet_sentiment_impact4', 'tweet_sentiment_impact5', 'social_score',
    # 'average_sentiment', 'sentiment_absolute', 'sentiment_relative', 'news',
    # 'medium', 'youtube', 'price_score', 'social_impact_score',
    # 'correlation_rank', 'galaxy_score', 'volatility', 'alt_rank',
    # 'volume_24h_rank', 'social_volume', 'price_btc', 'social_volume_global',
    # 'social_dominance', 'market_dominance', 'tweet_replies'
    #
    # market_cap = models.IntegerField(null=True)
    # url_shares = models.IntegerField(null=True)
    # unique_url_shares = models.IntegerField(null=True)
    # reddit_posts = models.IntegerField(null=True)
    # reddit_posts_score = models.IntegerField(null=True)
    # reddit_comments = models.IntegerField(null=True)
    # reddit_comments_score = models.IntegerField(null=True)
    # tweets = models.IntegerField(null=True)
    # tweet_spam = models.IntegerField(null=True)
    # tweet_followers = models.IntegerField(null=True)
    # tweet_quotes = models.IntegerField(null=True)
    # tweet_retweets = models.IntegerField(null=True)
    # tweet_replies = models.IntegerField(null=True)
    # tweet_favorites = models.IntegerField(null=True)
    # tweet_sentiment1 = models.IntegerField(null=True)
    # tweet_sentiment2 = models.IntegerField(null=True)
    # tweet_sentiment3 = models.IntegerField(null=True)
    # tweet_sentiment4 = models.IntegerField(null=True)
    # tweet_sentiment5 = models.IntegerField(null=True)
    # tweet_sentiment_impact1 = models.IntegerField(null=True)
    # tweet_sentiment_impact2 = models.IntegerField(null=True)
    # tweet_sentiment_impact3 = models.IntegerField(null=True)
    # tweet_sentiment_impact4 = models.IntegerField(null=True)
    # tweet_sentiment_impact5 = models.IntegerField(null=True)
    # social_score = models.IntegerField(null=True)
    # average_sentiment = models.FloatField(null=True)
    # sentiment_absolute = models.IntegerField(null=True)
    # sentiment_relative = models.IntegerField(null=True)
    # search_average = models.FloatField(null=True)
    # news = models.IntegerField(null=True)
    # medium = models.IntegerField(null=True)
    # youtube = models.IntegerField(null=True)
    # price_score = models.FloatField(null=True)
    # social_impact_score = models.FloatField(null=True)
    # correlation_rank = models.FloatField(null=True)
    # galaxy_score = models.FloatField(null=True)
    # volatility = models.FloatField(null=True)
    # alt_rank = models.IntegerField(null=True)
    # alt_rank_30d = models.IntegerField(null=True)
    # market_cap_rank = models.IntegerField(null=True)
    # percent_change_24h_rank = models.IntegerField(null=True)
    # volume_24h_rank = models.IntegerField(null=True)
    # social_volume_24h_rank = models.IntegerField(null=True)
    # social_score_24h_rank = models.IntegerField(null=True)
    # social_contributors = models.IntegerField(null=True)
    # social_volume = models.IntegerField(null=True)
    # price_btc = models.FloatField(null=True)
    # social_volume_global = models.IntegerField(null=True)
    # social_dominance = models.FloatField(null=True)
    # market_cap_global = models.IntegerField(null=True)
    # market_dominance = models.FloatField(null=True)
    # percent_change_24h = models.FloatField(null=True)

    class Meta:
        unique_together = ("open_time", "exchange", "interval", "symbol")


# class BotStatus(models.Model):
#
#     id = models.IntegerField(primary_key=True)
#     # status
