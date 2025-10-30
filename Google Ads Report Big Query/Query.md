


// Upload google ads keywords csv data to big query to create table

bq load \
    --source_format=CSV \
    --skip_leading_rows=3 \
    feisty-outrider-471302-k6:advanced_csv_analysis.search_keyword_report \
    "/home/zazikant/Search keyword report.csv" \
    Keyword_status:STRING,Keyword:STRING,Match_type:STRING,Campaign:STRING,Ad_group:STRING,Status:STRING,Status_reasons:STRING,Currency_code:STRING,Max_CPC:STRING,Final_URL:STRING,Avg_CPM:STRING,Interactions:STRING,Interaction_rate:STRING,Avg_cost:STRING,Cost:STRING,Impr:STRING,Clicks:STRING,Conv_rate:STRING,Conversions:STRING,Avg_CPC_1:STRING,Cost_per_conv:STRING




// Google Ads Conversion of numberic data to Numerics



SELECT
  * EXCEPT (
    Max_CPC,
    Avg_CPM,
    Interactions,
    Interaction_rate,
    Avg_cost,
    Cost,
    Impr,
    Clicks,
    Conv_rate,
    Conversions,
    Avg_CPC_1,
    Cost_per_conv
  )
FROM (
  SELECT
    *, -- Selects all original columns

    -- The following lines create cleaned, numeric versions for all relevant metrics
    SAFE_CAST(REPLACE(Clicks, ',', '') AS INT64) AS Clicks_numeric,
    SAFE_CAST(REPLACE(Cost, ',', '') AS FLOAT64) AS Cost_numeric,
    SAFE_CAST(REPLACE(Impr, ',', '') AS INT64) AS Impressions_numeric,
    SAFE_CAST(REPLACE(Max_CPC, ',', '') AS FLOAT64) AS Max_CPC_numeric,
    SAFE_CAST(REPLACE(Avg_CPM, ',', '') AS FLOAT64) AS Avg_CPM_numeric,
    SAFE_CAST(REPLACE(Interactions, ',', '') AS INT64) AS Interactions_numeric,
    SAFE_CAST(REPLACE(Interaction_rate, '%', '') AS FLOAT64) / 100 AS Interaction_rate_numeric,
    SAFE_CAST(REPLACE(Avg_cost, ',', '') AS FLOAT64) AS Avg_cost_numeric,
    SAFE_CAST(REPLACE(Conv_rate, '%', '') AS FLOAT64) / 100 AS Conv_rate_numeric,
    SAFE_CAST(REPLACE(Conversions, ',', '') AS FLOAT64) AS Conversions_numeric,
    SAFE_CAST(REPLACE(Avg_CPC_1, ',', '') AS FLOAT64) AS Avg_CPC_1_numeric,
    SAFE_CAST(REPLACE(Cost_per_conv, ',', '') AS FLOAT64) AS Cost_per_conv_numeric
  FROM
    `feisty-outrider-471302-k6.advanced_csv_analysis.search_keyword_report`
)