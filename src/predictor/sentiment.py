from transformers import pipeline


class Predictor:
    def __init__(self):
        # Set up the inference pipeline using a model from the 🤗 Hub
        self.sentiment_analysis = pipeline(
            model="finiteautomata/bertweet-base-sentiment-analysis"
        )

    def predict(self, tweet):
        # Let's run the sentiment analysis on each tweet
        sentiment = self.sentiment_analysis(tweet)
        return {
            "tweet": tweet,
            "label": sentiment[0]["label"],
            "pred_proba": sentiment[0]["score"],
        }
