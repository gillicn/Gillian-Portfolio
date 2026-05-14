#create table
CREATE OR REPLACE TABLE `quixotic-strand-474609-q2.moderation_analytics.moderation_analytic` AS
SELECT
  id,
  comment_text,
  CAST(toxic AS INT64) AS toxic,
  CAST(severe_toxic AS INT64) AS severe_toxic,
  CAST(obscene AS INT64) AS obscene,
  CAST(threat AS INT64) AS threat,
  CAST(insult AS INT64) AS insult,
  CAST(identity_hate AS INT64) AS identity_hate,

#create toxic_flag column to identify which id is flagged as toxic
  CASE
    WHEN CAST(toxic AS INT64) = 1
      OR CAST(severe_toxic AS INT64) = 1
      OR CAST(obscene AS INT64) = 1
      OR CAST(threat AS INT64) = 1
      OR CAST(insult AS INT64) = 1
      OR CAST(identity_hate AS INT64) = 1
    THEN 1
    ELSE 0
  END AS toxic_flag,

   LENGTH(comment_text) AS comment_length,

  ARRAY_LENGTH(SPLIT(TRIM(comment_text), ' ')) AS word_count
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_analytic`
WHERE comment_text IS NOT NULL;

#add simulated moderation prediction, predicted_toxic 
CREATE OR REPLACE TABLE `quixotic-strand-474609-q2.moderation_analytics.moderation_prediction` AS
SELECT
  *,
  CASE
    WHEN LOWER(comment_text) LIKE '%idiot%' THEN 1
    WHEN LOWER(comment_text) LIKE '%stupid%' THEN 1
    WHEN LOWER(comment_text) LIKE '%hate%' THEN 1
    WHEN LOWER(comment_text) LIKE '%kill%' THEN 1
    WHEN LOWER(comment_text) LIKE '%moron%' THEN 1
    WHEN LOWER(comment_text) LIKE '%trash%' THEN 1
    WHEN LOWER(comment_text) LIKE '%dumb%' THEN 1
    WHEN LOWER(comment_text) LIKE '%shut up%' THEN 1
    WHEN LOWER(comment_text) LIKE '%ugly%' THEN 1
    WHEN LOWER(comment_text) LIKE '%loser%' THEN 1
    ELSE 0
  END AS predicted_toxic
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_analytic`;

#creating error type table
CREATE OR REPLACE TABLE `quixotic-strand-474609-q2.moderation_analytics.moderation_final` AS
SELECT
  *,
  CASE
    WHEN predicted_toxic = 1 AND toxic_flag = 1 THEN 'True Positive'
    WHEN predicted_toxic = 0 AND toxic_flag = 0 THEN 'True Negative'
    WHEN predicted_toxic = 1 AND toxic_flag = 0 THEN 'False Positive'
    WHEN predicted_toxic = 0 AND toxic_flag = 1 THEN 'False Negative'
    ELSE 'Unknown'
  END AS error_type
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_prediction`;

#calculating total comments and toxicity rate 
SELECT
  COUNT(*) AS total_comments,
  SUM(toxic_flag) AS toxic_comments,
  ROUND(SAFE_DIVIDE(SUM(toxic_flag), COUNT(*)) * 100, 2) AS toxicity_rate_percent
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`;
#total comments: 159571, toxic_comments: 16225, toxicity rate percentage: 10.17%

#distribution of toxic categories
SELECT 'toxic' AS category, SUM(toxic) AS total
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`
UNION ALL
SELECT 'severe_toxic', SUM(severe_toxic)
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`
UNION ALL
SELECT 'obscene', SUM(obscene)
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`
UNION ALL
SELECT 'threat', SUM(threat)
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`
UNION ALL
SELECT 'insult', SUM(insult)
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`
UNION ALL
SELECT 'identity_hate', SUM(identity_hate)
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`;
#toxic: 15294, severe toxic: 1595, obscene: 8449, threat: 478, insult: 7877, identity hate: 1405

#average comment length by toxicity
SELECT
  toxic_flag,
  ROUND(AVG(comment_length), 2) AS avg_comment_length,
  ROUND(AVG(word_count), 2) AS avg_word_count
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`
GROUP BY toxic_flag
ORDER BY toxic_flag;
#toxic flag 0: average comment length: 404.35, average word count: 69.53 
#toxic flag 1: average comment length: 303.3, average word count: 53.15

#error type breakdown
SELECT
  error_type,
  COUNT(*) AS total
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`
GROUP BY error_type
ORDER BY total DESC;
#true negative: 137473, false negative: 12314, false positive: 5873, true positive: 3911

#accuracy
SELECT
  ROUND(
    SAFE_DIVIDE(
      SUM(CASE WHEN error_type IN ('True Positive', 'True Negative') THEN 1 ELSE 0 END),
      COUNT(*)
    ) * 100, 2
  ) AS accuracy_percent
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`;
#accuracy percentage: 88.6

#false positive rate
SELECT
  ROUND(
    SAFE_DIVIDE(
      SUM(CASE WHEN error_type = 'False Positive' THEN 1 ELSE 0 END),
      SUM(CASE WHEN toxic_flag = 0 THEN 1 ELSE 0 END)
    ) * 100,
    2
  ) AS false_positive_rate_percent
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`;
#false positive rate: 4.1

#false negative rate
SELECT
  ROUND(
    SAFE_DIVIDE(
      SUM(CASE WHEN error_type = 'False Negative' THEN 1 ELSE 0 END),
      SUM(CASE WHEN toxic_flag = 1 THEN 1 ELSE 0 END)
    ) * 100,
    2
  ) AS false_negative_rate_percent
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`;
#false negative rate: 75.9

#precision
SELECT
  ROUND(
    SAFE_DIVIDE(
      SUM(CASE WHEN error_type = 'True Positive' THEN 1 ELSE 0 END),
      SUM(CASE WHEN predicted_toxic = 1 THEN 1 ELSE 0 END)
    ) * 100,
    2
  ) AS precision_percent
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`;
#precision percentage: 39.97

#recall
SELECT
  ROUND(
    SAFE_DIVIDE(
      SUM(CASE WHEN error_type = 'True Positive' THEN 1 ELSE 0 END),
      SUM(CASE WHEN toxic_flag = 1 THEN 1 ELSE 0 END)
    ) * 100,
    2
  ) AS recall_percent
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`;
#recall percentage: 24.1

#false negatives summary
SELECT
  COUNT(*) AS total_false_negatives,
  ROUND(AVG(comment_length), 2) AS avg_length,
  ROUND(AVG(word_count), 2) AS avg_words
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`
WHERE error_type = 'False Negative';
#total false negative: 12314, average length: 268.38, average words: 46.68

#false positive summary
SELECT
  COUNT(*) AS total_false_positives,
  ROUND(AVG(comment_length), 2) AS avg_length,
  ROUND(AVG(word_count), 2) AS avg_words
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`
WHERE error_type = 'False Positive';
#total false positive: 5873, average length: 1096.93, average word: 188.64

#toxic labels that appear most in false negatives
SELECT
  SUM(toxic) AS toxic_count,
  SUM(severe_toxic) AS severe_toxic_count,
  SUM(obscene) AS obscene_count,
  SUM(threat) AS threat_count,
  SUM(insult) AS insult_count,
  SUM(identity_hate) AS identity_hate_count
FROM `quixotic-strand-474609-q2.moderation_analytics.moderation_final`
WHERE error_type = 'False Negative';
#toxic: 11601, severe_toxic: 1266, obscene: 6566, threat: 292, insult: 5585