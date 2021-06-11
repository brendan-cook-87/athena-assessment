import sys
from awsglue.transforms import Join
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql.functions import to_date
import boto3

glueContext = GlueContext(SparkContext.getOrCreate())

input_dir = 's3://bcook-assessment/input-dir/'
output_dir = 's3://bcook-assessment/output-dir/'

glueContext.purge_s3_path(output_dir)

acc_entry = f'{input_dir}/Accounting_Entry.csv'
equ_owner = f'{input_dir}/Equitable_Owner.csv'
equ_owner_hist = f'{input_dir}/Equitable_Owner_History.csv'

acc_entry_df = glueContext.create_dynamic_frame.from_options(
    connection_type = 's3',
    connection_options = {
        'paths': [acc_entry]
    },
    format='csv',
    format_options={
        "withHeader": True
    }
)

equ_owner_df = glueContext.create_dynamic_frame.from_options(
    connection_type = 's3',
    connection_options = {
        'paths': [equ_owner]
    },
    format='csv',
    format_options={
        "withHeader": True
    }
)

equ_owner_hist_df = glueContext.create_dynamic_frame.from_options(
    connection_type = 's3',
    connection_options = {
        'paths': [equ_owner_hist]
    },
    format='csv',
    format_options={
        "withHeader": True
    }
)

loan_account_df = DynamicFrame.fromDF(
    acc_entry_df.select_fields('Id').toDF().dropDuplicates(),
    glueContext,
    'loan_account_df'
    )


acc_entry_df = DynamicFrame.fromDF(
    acc_entry_df.toDF().withColumn('transaction_date', to_date('transaction_date', 'yyyy-MM-dd')),
    glueContext,
    'acc_entry_df'
)

acc_entry_df = acc_entry_df.applyMapping(
    [
        ('id', 'varchar', 'id', 'varchar'),
        ('transaction_date', 'date', 'transaction_date', 'date'),
        ('loan_account_id', 'varchar', 'loan_account_id', 'varchar'),
        ('credit_amount', 'varchar', 'credit_amount', 'double'),
        ('credit_gl_account_code', 'varchar', 'credit_gl_account_code', 'integer'),
        ('debit_amount', 'varchar', 'debit_amount', 'double'),
        ('debit_gl_account_code', 'varchar', 'debit_gl_account_code', 'integer')
    ]
)

equ_owner_hist_df = DynamicFrame.fromDF(
    equ_owner_hist_df.toDF().withColumn('reallocation_date', to_date('reallocation_date', 'yyyy-MM-dd')),
    glueContext,
    'equ_owner_hist_df'
)

equ_owner_hist_df = equ_owner_hist_df.applyMapping(
    [
        ('reallocation_date', 'date', 'reallocation_date', 'date'),
        ('loan_account_id', 'varchar', 'loan_account_id', 'varchar'),
        ('from_equitable_owner_id', 'varchar', 'from_equitable_owner_id', 'varchar'),
        ('equitable_owner_id', 'varchar', 'equitable_owner_id', 'varchar')
    ]
)

glueContext.write_dynamic_frame.from_options(
    frame = equ_owner_df,
    connection_type = 's3',
    connection_options = {"path": f'{output_dir}/equitable_owner'},
    format = "parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame = acc_entry_df,
    connection_type = 's3',
    connection_options = {"path": f'{output_dir}/accounting_entry'},
    format = "parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame = loan_account_df,
    connection_type = 's3',
    connection_options = {"path": f'{output_dir}/loan_account'},
    format = "parquet"
)

glueContext.write_dynamic_frame.from_options(
    frame = equ_owner_hist_df,
    connection_type = 's3',
    connection_options = {"path": f'{output_dir}/equitable_owner_history'},
    format = "parquet"
)

