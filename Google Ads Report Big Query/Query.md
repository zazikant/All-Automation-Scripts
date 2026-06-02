Step 1: Get CSV into Google Sheets [2 min]
Go to https://sheets.google.com
File → Import → Upload → drag your Search keyword report.csv
Import settings:
Separator type: Detect automatically
Convert text to numbers, dates, and formulas: Yes
Important: 
1. **Delete the first 2 rows Google Ads adds as junk headers, so row 1 = Keywordstatus, Keyword, Matchtype...**
2**. Delete the last unnecessary rows of totals**

Step 2: Connect Looker Studio to that Sheet
Go to https://lookerstudio.google.com
Create → Report
Add data → Google Sheets → pick your uploaded sheet
Select the worksheet + check Use first row as headers
Add → Add to report

Step 3: Fix data types in Looker Studio
Looker Studio will import everything as Text. Change these:

Go to PAGE -> Page settings (to change the data type / manage data)

Field	Change to
Cost	Currency USD
Clicks, Impr, Conversions	Number
Convrate, Interactionrate	Percent
MaxCPC, AvgCPC1, Avgcost	Currency USD

** In manage data -> For Avg fields.. "Default Aggregation" change to Average instead of SUM **

2 different reports are made with individual csv for "search terms report" and "search keyword report"


# == Below method is for biq query above method is for csv ==

Inside **data studio** (==shashikantzarekar@gmail.com==) , TO change the "source" of data in Big Query, go to Page > Current Page settings > on right select data source.

--------------------- *** FOR KEYWORD data to big query (have filter on "keywords" and put efforts to analyse performance) *** ---------------

// Use gemini cli (shashikantzarekar@gmail.com  gcloud projects list and gcloud config set project feisty-outrider-471302-k6) and do this: Upload google ads keywords csv data to big query to create table

bq load \
    --source_format=CSV \
    --skip_leading_rows=3 \
    feisty-outrider-471302-k6:advanced_csv_analysis.search_keyword_report \
    "/home/shashikantzarekar/Search keyword report.csv" \
    Keyword_status:STRING,Keyword:STRING,Match_type:STRING,Campaign:STRING,Ad_group:STRING,Status:STRING,Status_reasons:STRING,Currency_code:STRING,Max_CPC:STRING,Final_URL:STRING,Avg_CPM:STRING,Interactions:STRING,Interaction_rate:STRING,Avg_cost:STRING,Cost:STRING,Impr:STRING,Clicks:STRING,Conv_rate:STRING,Conversions:STRING,Avg_CPC_1:STRING,Cost_per_conv:STRING


// Google Ads Conversion of numberic data to Numerics (Same query to paste in data studio> big query > custom query)

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

TO remove previous data source, go to Resource - Manage added data sources - remove top one.

----------------------


*** FOR Search terms data to big query (have filter of "search term" and do efforts to find right keywords) ***

// go to [shell.cloud.google.com](shell.cloud.google.com) and click on top right `>_`.  Then upload csv in explorer. Then do gcloud auth login in shell. Then paste this line to create table.

bq load \
    --source_format=CSV \
    --skip_leading_rows=3 \
    feisty-outrider-471302-k6:advanced_csv_analysis.search_terms_report \
    "/home/shashikantzarekar/Search terms report.csv" \
    Search_term:STRING,Match_type:STRING,Added_Excluded:STRING,Campaign:STRING,Ad_group:STRING,Keyword:STRING,Currency_code:STRING,Avg_CPM:STRING,Impr:STRING,Interactions:STRING,Interaction_rate:STRING,Avg_cost:STRING,Cost:STRING,Campaign_type:STRING,Conv_rate:STRING,Conversions:STRING,Cost_per_conv:STRING


// Google Ads Conversion of numberic data to Numerics (Same query to paste in data studio > big query > custom query)

SELECT
  -- Text Dimensions
  Search_term,
  Match_type,
  Added_Excluded,
  Campaign,
  Ad_group,
  Keyword,
  Currency_code,
  Campaign_type,

  -- Cleaned Numeric Metrics
  SAFE_CAST(REPLACE(Avg_CPM, ',', '') AS FLOAT64) AS Avg_CPM,
  SAFE_CAST(REPLACE(Impr, ',', '') AS INT64) AS Impressions,
  SAFE_CAST(REPLACE(Interactions, ',', '') AS INT64) AS Interactions,
  SAFE_CAST(REPLACE(Interaction_rate, '%', '') AS FLOAT64) / 100 AS Interaction_rate,
  SAFE_CAST(REPLACE(Avg_cost, ',', '') AS FLOAT64) AS Avg_cost,
  SAFE_CAST(REPLACE(Cost, ',', '') AS FLOAT64) AS Cost,
  SAFE_CAST(REPLACE(Conv_rate, '%', '') AS FLOAT64) / 100 AS Conv_rate,
  SAFE_CAST(REPLACE(Conversions, ',', '') AS FLOAT64) AS Conversions,
  SAFE_CAST(REPLACE(Cost_per_conv, ',', '') AS FLOAT64) AS Cost_per_conv
FROM
  `feisty-outrider-471302-k6.advanced_csv_analysis.search_terms_report`

----------------------








