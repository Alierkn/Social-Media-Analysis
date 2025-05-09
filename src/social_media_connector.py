import tweepy
import praw
import time
import json
import logging
from textblob import TextBlob
from datetime import datetime, timedelta
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SocialMediaConnector:
    def __init__(self, twitter_credentials=None, reddit_credentials=None):
        self.twitter_api = None
        self.reddit_api = None
        
        # Twitter API kurulumu
        if twitter_credentials:
            try:
                auth = tweepy.OAuthHandler(
                    twitter_credentials["consumer_key"],
                    twitter_credentials["consumer_secret"]
                )
                auth.set_access_token(
                    twitter_credentials["access_token"],
                    twitter_credentials["access_token_secret"]
                )
                self.twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
                logger.info("Twitter API connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Twitter API: {e}")
        
        # Reddit API kurulumu
        if reddit_credentials:
            try:
                self.reddit_api = praw.Reddit(
                    client_id=reddit_credentials["client_id"],
                    client_secret=reddit_credentials["client_secret"],
                    user_agent=reddit_credentials["user_agent"],
                    username=reddit_credentials.get("username", ""),
                    password=reddit_credentials.get("password", "")
                )
                logger.info("Reddit API connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Reddit API: {e}")
    
    def analyze_sentiment(self, text):
        """Metin duygu analizi"""
        blob = TextBlob(text)
        return blob.sentiment.polarity
    
    def search_twitter(self, query, count=100):
        """Twitter'da arama yap ve sonuçları döndür"""
        if not self.twitter_api:
            logger.error("Twitter API connection not available")
            return []
        
        try:
            tweets = []
            for tweet in tweepy.Cursor(self.twitter_api.search_tweets, q=query, lang="en", tweet_mode="extended").items(count):
                # Yeniden tweetleri atlayalım
                if hasattr(tweet, "retweeted_status"):
                    continue
                    
                tweet_data = {
                    "id": tweet.id_str,
                    "user_id": tweet.user.id_str,
                    "user_name": tweet.user.screen_name,
                    "user_followers": tweet.user.followers_count,
                    "content": tweet.full_text,
                    "created_at": tweet.created_at,
                    "retweet_count": tweet.retweet_count,
                    "favorite_count": tweet.favorite_count,
                    "platform": "twitter"
                }
                
                # Duygu analizi ekleyelim
                tweet_data["sentiment"] = self.analyze_sentiment(tweet.full_text)
                
                # Hashtag'leri ekleyelim
                if hasattr(tweet, "entities") and "hashtags" in tweet.entities:
                    tweet_data["hashtags"] = [tag["text"] for tag in tweet.entities["hashtags"]]
                
                # Mentions ekleyelim 
                if hasattr(tweet, "entities") and "user_mentions" in tweet.entities:
                    tweet_data["mentions"] = [mention["screen_name"] for mention in tweet.entities["user_mentions"]]
                
                tweets.append(tweet_data)
                
            logger.info(f"Retrieved {len(tweets)} tweets for query: {query}")
            return tweets
        except Exception as e:
            logger.error(f"Error searching Twitter: {e}")
            return []
    
    def search_reddit(self, subreddit_name, limit=100, time_filter="week"):
        """Reddit'te belirli bir subreddit'te arama yap"""
        if not self.reddit_api:
            logger.error("Reddit API connection not available")
            return []
        
        try:
            posts = []
            subreddit = self.reddit_api.subreddit(subreddit_name)
            
            for post in subreddit.top(time_filter=time_filter, limit=limit):
                post_data = {
                    "id": post.id,
                    "user_id": post.author.name if post.author else "[deleted]",
                    "title": post.title,
                    "content": post.selftext,
                    "created_at": datetime.fromtimestamp(post.created_utc),
                    "score": post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comments": post.num_comments,
                    "url": post.url,
                    "platform": "reddit",
                    "subreddit": subreddit_name
                }
                
                # Duygu analizi ekleyelim
                post_data["sentiment"] = self.analyze_sentiment(post.title + " " + post.selftext)
                
                posts.append(post_data)
            
            logger.info(f"Retrieved {len(posts)} posts from r/{subreddit_name}")
            return posts
        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            return []
    
    def get_reddit_comments(self, post_id, limit=None):
        """Belirli bir Reddit gönderisinin yorumlarını al"""
        if not self.reddit_api:
            logger.error("Reddit API connection not available")
            return []
        
        try:
            comments = []
            submission = self.reddit_api.submission(id=post_id)
            submission.comments.replace_more(limit=limit)
            
            for comment in submission.comments.list():
                comment_data = {
                    "id": comment.id,
                    "post_id": post_id,
                    "user_id": comment.author.name if comment.author else "[deleted]",
                    "content": comment.body,
                    "created_at": datetime.fromtimestamp(comment.created_utc),
                    "score": comment.score,
                    "platform": "reddit",
                    "parent_id": comment.parent_id
                }
                
                # Duygu analizi ekleyelim
                comment_data["sentiment"] = self.analyze_sentiment(comment.body)
                
                comments.append(comment_data)
            
            logger.info(f"Retrieved {len(comments)} comments for post {post_id}")
            return comments
        except Exception as e:
            logger.error(f"Error getting Reddit comments: {e}")
            return []
    
    def identify_influencers(self, data, platform):
        """Etkileyen kullanıcıları tanımla"""
        if not data:
            return []
        
        df = pd.DataFrame(data)
        
        if platform == "twitter":
            # For Twitter, sort by follower count, retweets and favorites
            if "user_followers" in df.columns and "retweet_count" in df.columns and "favorite_count" in df.columns:
                df["engagement"] = df["retweet_count"] + df["favorite_count"]
                df["influence_score"] = df["user_followers"] * 0.6 + df["engagement"] * 0.4
                
                influencers = df.sort_values(by="influence_score", ascending=False)
                return influencers[["user_id", "user_name", "user_followers", "influence_score"]].drop_duplicates(subset=["user_id"]).head(10).to_dict("records")
        
        elif platform == "reddit":
            # For Reddit, post score and comment count
            if "score" in df.columns and "num_comments" in df.columns:
                df["influence_score"] = df["score"] * 0.7 + df["num_comments"] * 0.3
                
                influencers = df.sort_values(by="influence_score", ascending=False)
                return influencers[["user_id", "score", "num_comments", "influence_score"]].drop_duplicates(subset=["user_id"]).head(10).to_dict("records")
        
        return []
    
    def analyze_trends(self, data, platform, time_window_days=7):
        """Trend analizi yap"""
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        
        # Tarih sütununu datetime'a dönüştürelim
        if "created_at" in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df["created_at"]):
                df["created_at"] = pd.to_datetime(df["created_at"])
            
            # Filter data from the last X days
            now = datetime.now()
            start_date = now - timedelta(days=time_window_days)
            df = df[df["created_at"] >= start_date]
            
            # Günlük aktivite
            df["date"] = df["created_at"].dt.date
            daily_activity = df.groupby("date").size().reset_index(name="count")
            daily_activity = daily_activity.sort_values(by="date")
            
            trends = {
                "daily_activity": daily_activity.to_dict("records")
            }
            
            # Hashtag analysis for Twitter
            if platform == "twitter" and "hashtags" in df.columns:
                # Tüm hashtag'leri düzleştirelim
                all_hashtags = []
                for hashtag_list in df["hashtags"].dropna():
                    all_hashtags.extend(hashtag_list)
                
                # En popüler hashtag'leri bulalım
                if all_hashtags:
                    hashtag_counts = pd.Series(all_hashtags).value_counts().head(10)
                    trends["top_hashtags"] = [{"hashtag": tag, "count": count} 
                                             for tag, count in hashtag_counts.items()]
            
            # Duygu analizi trendleri
            if "sentiment" in df.columns:
                df["sentiment_category"] = pd.cut(
                    df["sentiment"],
                    bins=[-1, -0.3, 0.3, 1],
                    labels=["Negative", "Neutral", "Positive"]
                )
                
                sentiment_counts = df["sentiment_category"].value_counts().reset_index()
                sentiment_counts.columns = ["sentiment", "count"]
                trends["sentiment_distribution"] = sentiment_counts.to_dict("records")
                
                # Sentiment change over time
                sentiment_over_time = df.groupby("date")["sentiment"].mean().reset_index()
                trends["sentiment_over_time"] = sentiment_over_time.to_dict("records")
            
            return trends
        
        return {}

# Test amaçlı kullanım
if __name__ == "__main__":
    # Bu kısım sadece test amaçlıdır ve gerçek API anahtarları gerektirir
    print("Social Media Connector module loaded")
