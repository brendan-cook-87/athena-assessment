provider "aws" {
  region                  = "ap-southeast-2"
  shared_credentials_file = "C:\\Users\\bcook\\.aws\\credentials"
  profile                 = "bcook"
}

resource "aws_s3_bucket" "bcook_assessment_bucket" {
    bucket = "bcook-assessment"
    acl    = "private"
    versioning {
        enabled = true
    }
}

resource "aws_s3_bucket_object" "ETL_Code" {
  bucket = aws_s3_bucket.bcook_assessment_bucket.id
  key    = "etl.py"
  source = "etl.py"
  etag = filemd5("etl.py")
}

resource "aws_s3_bucket_object" "Lambda_Code" {
  bucket = aws_s3_bucket.bcook_assessment_bucket.id
  key    = "lambda.py"
  source = "lambda.py"
  etag = filemd5("etl.py")
}

resource "aws_s3_bucket_object" "Accounting_Entry" {
  bucket = aws_s3_bucket.bcook_assessment_bucket.id
  key    = "input-dir/Accounting_Entry.csv"
  source = "Accounting_Entry.csv"
  etag = filemd5("Accounting_Entry.csv")
}

resource "aws_s3_bucket_object" "Equitable_Owner" {
  bucket = aws_s3_bucket.bcook_assessment_bucket.id
  key    = "input-dir/Equitable_Owner.csv"
  source = "Equitable_Owner.csv"
  etag = filemd5("Equitable_Owner.csv")
}

resource "aws_s3_bucket_object" "Equitable_Owner_History" {
  bucket = aws_s3_bucket.bcook_assessment_bucket.id
  key    = "input-dir/Equitable_Owner_History.csv"
  source = "Equitable_Owner_History.csv"
  etag = filemd5("Equitable_Owner_History.csv")
}

resource "aws_glue_job" "Assessment_ETL" {
    name = "Assessment_ETL"
    glue_version = "2.0"
    worker_type = "G.1X"
    number_of_workers = "5"
    role_arn = "arn:aws:iam::590706858940:role/service-role/AWSGlueServiceRole-bcook"

    command {
        script_location = "s3://bcook-assessment/etl.py"
        python_version = "3"
    }

    default_arguments = {
        # ... potentially other arguments ...
        "--job-bookmark-option" = "job-bookmark-disable"
        "--job-language" = "python"
        "--enable-glue-datacatalog" = ""
        "--enable-continuous-cloudwatch-log" = "true"
        "--enable-continuous-log-filter"     = "true"
        "--enable-metrics"                   = "true"
    }
}

resource "aws_glue_crawler" "CatalogCrawler" {
  database_name = "bcook-assessment"
  name          = "CatalogCrawler"
  role          = "arn:aws:iam::590706858940:role/service-role/AWSGlueServiceRole-bcook"

  s3_target {
    path = "s3://bcook-assessment/output-dir"
  }

   schema_change_policy {
    delete_behavior = "LOG"
  }

}

resource "aws_glue_workflow" "etl_workflow" {
  name = "etl_workflow"
}

resource "aws_glue_trigger" "etl_start" {
  name          = "etl_start"
  workflow_name = aws_glue_workflow.etl_workflow.name
  type          = "ON_DEMAND"

  actions {
    job_name = aws_glue_job.Assessment_ETL.name
  }

}

resource "aws_glue_trigger" "etl_end" {
  name          = "trigger-crawler"
  type          = "CONDITIONAL"
  workflow_name = aws_glue_workflow.etl_workflow.name

  predicate {
    conditions {
      job_name = aws_glue_job.Assessment_ETL.name
      state    = "SUCCEEDED"
    }
  }

  actions {
    crawler_name = aws_glue_crawler.CatalogCrawler.name
  }
}


resource "aws_glue_crawler" "LogsCrawler" {
  database_name = "bcook-assessment"
  name          = "LogsCrawler"
  role          = "arn:aws:iam::590706858940:role/service-role/AWSGlueServiceRole-bcook"
  schedule      = "cron(0/15 * * * ? *)"

  s3_target {
    path = "s3://bcook-assessment/logs"
  }
}