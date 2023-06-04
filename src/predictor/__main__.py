from .sentiment import Predictor

if __name__ == "__main__":
    # kafka_consumer =
    tweet = "__placeholder"
    predictor = Predictor()
    result = predictor.predict(tweet)
