USE SCHEMA gold;
CREATE OR REPLACE MATERIALIZED VIEW dim_date AS
WITH date_series AS (
  SELECT explode(sequence(to_date('2000-01-01'), to_date('2100-12-31'), interval 1 day)) AS date
)
SELECT
  cast(date_format(date, 'yyyyMMdd') as int) AS date_key,
  date AS full_date,
  year(date) AS year,
  quarter(date) AS quarter,
  month(date) AS month,
  day(date) AS day,
  dayofweek(date) AS day_of_week,
  date_format(date, 'EEEE') AS day_name,
  date_format(date, 'MMMM') AS month_name,
  weekofyear(date) AS week_of_year,
  dayofyear(date) AS day_of_year,
  CASE WHEN dayofweek(date) IN (1,7) THEN 1 ELSE 0 END AS is_weekend,
  CASE WHEN dayofweek(date) BETWEEN 2 AND 6 THEN 1 ELSE 0 END AS is_weekday,
  concat('Q', quarter(date)) AS quarter_name,
  concat(year(date), ' Q', quarter(date)) AS year_quarter,
  date_format(date, 'yyyy-MM') AS year_month,
  date_sub(date, dayofweek(date) - 1) AS week_start_date,
  date_add(date_sub(date, dayofweek(date) - 1), 6) AS week_end_date,
  date_trunc('month', date) AS month_start_date,
  last_day(date) AS month_end_date,
  date_trunc('quarter', date) AS quarter_start_date,
  date_sub(date_add(MONTH, 3, date_trunc('quarter', date)), 1) AS quarter_end_date,
  date_trunc('year', date) AS year_start_date,
  date_sub(date_add(YEAR, 1, date_trunc('year', date)), 1) AS year_end_date
FROM date_series;