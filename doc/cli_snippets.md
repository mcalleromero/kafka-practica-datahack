# KSQLDB

```
CREATE STREAM sentimentTweets (
    user VARCHAR, 
    content VARCHAR, 
    date VARCHAR,
    timestamp VARCHAR,
    sentiment STRUCT<label VARCHAR, 
        pred_proba DOUBLE>
) WITH (
    kafka_topic='stream-sentiment', 
    value_format='json',
    timestamp = 'date',
    timestamp_format='yyyy-MM-dd''T''HH:mm:ss''Z'''
);
```

```
CREATE TABLE numberOfTweets AS
SELECT sentiment->label,
       count(*) AS numberOfTweets
FROM sentimentTweets
GROUP BY sentiment->label;
```

```
SELECT *
FROM numberOfTweets;
```

```
SELECT user, content, sentiment->label
FROM sentimentTweets
WHERE sentiment->label = 'POS'
EMIT CHANGES;
```