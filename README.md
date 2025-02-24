# Lake-in-House Project Specification

## Overview
- **Objective:**  
  Group commonly used data tools into a single project to enhance my learning, leveraging project-building as the best way to master new technologies.  
- **Stakeholders:**  
  - Me  
  - Myself  
  - Flavio Pegas  
- **Pipeline Owner:**  
  Flaviodiasps@gmail.com
- **Sponsor:**  
  Flavio - Director of this github repository  
- **Start Date:**  
  February 21, 2025  
- **Due Date:**  
  March 14, 2025 (I gave me a 3-week timeline)  

## Scope

### Business Metrics
- **In-Scope:**  
    |Metric|Definition|is_guardrail|
    |-|-|-|
    |customer_id|String|Unique customer ID|
    |date|Date|Transaction date|
    |amount|Float|Transaction amount|

- **Out-of-Scope:**  
  - Business questions and assumptions not addressed, I will add it after I analyse the data 

### Architecture Scope
- **In-Scope:**  
  Simulate a streaming scenario with the following flow:  
  - **Source:** Stream data row-by-row from a local CSV file to a PostgreSQL database (Docker).  
  - **CDC:** Enable Change Data Capture (CDC) with Debezium on Kafka Connect, sending JSON data to Kafka.  
  - **Consumption:**  
    - **Streaming (Append-Only):**  
      - Aggregate JSONs and ingest into PostgreSQL (Docker).  
      - Create a visualization in Grafana (Docker).  
    - **Batch (Merge):**  
      - Aggregate JSONs using Flink and store on a local Docker volume as array of jsons.  
      - Manually upload data to Azure Data Lake Storage Gen2 (ADLS2).  
      - Build Databricks Delta Live Tables (DLT) pipelines for bronze, silver, and gold tables.  
  - **Version Control:** All code will be tracked in this public GitHub repository.  
- **Out-of-Scope:**  
  - No CI/CD pipelines  
  - No Databricks DABs (Data Analytics Bricks)  
  - No security measures  

## Data
- **Input:**  
  - Source: table
    - Schema: `customer_id, date, amount` (example)  
  - Source: table2
    - Schema: `customer_id, date, amount` (example)   
- **Transforms:**  
  - Parse dates, enrich (example)  
- **Output:**  
  - Destination: `processed_data` (example)  
  - Format: Delta (example)  
  - **Schema:**  
    |Name|Type|Comment|
    |-|-|-|
    |customer_id|String|Unique customer ID|
    |date|Date|Transaction date|
    |amount|Float|Transaction amount|

- **Quality Checks:**  
  - Null check on `customer_id`  
  - Date format validation (`YYYY-MM-DD`)  
  - Amount must be positive (> 0)
  - Dedup

## Requirements
- **Timelines:**  
  - Streaming data: Must arrive within 10 minutes  
  - Batch data: Must be ready daily by 9:00 AM  
- **Retention:**  
  - No retention requirements  

## Error & Monitoring
- **Errors:**  
  - Pipeline halts on any error; bad data must not reach production.  
- **Monitoring:**  
  - Flink logs sent to Elasticsearch in local Docker  
  - Databricks logs remain in Databricks  
  - DQX will be used for data quality monitoring  

## Security
- **Access:**  
  - No security measures implemented  

## Risks
- **Assumptions:**  
  - There’s a risk of something going wrong  

## Support
- **Documentation:**  
  - This right here, is the doc