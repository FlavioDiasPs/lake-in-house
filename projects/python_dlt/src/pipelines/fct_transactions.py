# import dlt


# sales_schema = StructType([
#   StructField("customer_id", StringType(), True),
#   StructField("customer_name", StringType(), True),
#   StructField("number_of_line_items", StringType(), True),
#   StructField("order_datetime", StringType(), True),
#   StructField("order_number", LongType(), True)]
# )

# @dlt.table(
#   comment="Raw data on sales",
#   schema="""
#     customer_id STRING,
#     customer_name STRING,
#     number_of_line_items STRING,
#     order_datetime STRING,
#     order_number LONG,
#     order_day_of_week STRING GENERATED ALWAYS AS (dayofweek(order_datetime))
#     """,
#   cluster_by = ["order_day_of_week", "customer_id"])
# def sales():
#   return ("...")


# @dlt.table(
#    schema="""
#     customer_id STRING NOT NULL PRIMARY KEY,
#     customer_name STRING,
#     number_of_line_items STRING,
#     order_datetime STRING,
#     order_number LONG,
#     order_day_of_week STRING GENERATED ALWAYS AS (dayofweek(order_datetime)),
#     CONSTRAINT fk_customer_id FOREIGN KEY (customer_id) REFERENCES main.default.customers(customer_id)
#     """
# def sales():
#    return ("...")


#    @dlt.table(
#    schema="""
#     id int COMMENT 'This is the customer ID',
#     name string COMMENT 'This is the customer full name',
#     region string,
#     ssn string MASK catalog.schema.ssn_mask_fn USING COLUMNS (region)
#     """,
#   row_filter = "ROW FILTER catalog.schema.us_filter_fn ON (region, name)"
# def sales():
#    return ("...")


# @dlt.table(
#   name="<name>",
#   comment="<comment>",
#   spark_conf={"<key>" : "<value>", "<key>" : "<value>"},
#   table_properties={"<key>" : "<value>", "<key>" : "<value>"},
#   path="<storage-location-path>",
#   partition_cols=["<partition-column>", "<partition-column>"],
#   cluster_by = ["<clustering-column>", "<clustering-column>"],
#   schema="schema-definition",
#   row_filter = "row-filter-clause",
#   temporary=False)
# @dlt.expect
# @dlt.expect_or_fail
# @dlt.expect_or_drop
# @dlt.expect_all
# @dlt.expect_all_or_drop
# @dlt.expect_all_or_fail
# def <function-name>():
#     return (<query>)
