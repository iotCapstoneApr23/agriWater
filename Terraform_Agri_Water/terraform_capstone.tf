# Configure the AWS Provider
provider "aws" {
  region = "us-east-1" # Replace with your desired AWS region
}

# Create the IoT Core Thing
# resource "aws_iot_thing" "soil_sensor" {
#   name = "SoilSensor"
# }

# Create the IoT Rule
resource "aws_iot_topic_rule" "capstone_IoT2Kinesis_Rule_WS_01" {
  name        = "capstone_IoT2Kinesis_Rule_WS_01"
  enabled     = true
  sql         = "SELECT * FROM 'iot/ss' WHERE sprinkler_id = 'WS_01'"
  sql_version = "2016-03-23"

  kinesis {
    role_arn     = aws_iam_role.capstone_IoT2Kinesis_Role.arn
    stream_name  = aws_kinesis_stream.Agri_Water.name
    partition_key = "Sprinkler_01"
  }
}

resource "aws_iot_topic_rule" "capstone_IoT2Kinesis_Rule_WS_02" {
  name        = "capstone_IoT2Kinesis_Rule_WS_02"
  enabled     = true
  sql         = "SELECT * FROM 'iot/ss' WHERE sprinkler_id = 'WS_02'"
  sql_version = "2016-03-23"

  kinesis {
    role_arn     = aws_iam_role.capstone_IoT2Kinesis_Role.arn
    stream_name  = aws_kinesis_stream.Agri_Water.name
    partition_key = "Sprinkler_02"
  }
}

resource "aws_iot_topic_rule" "capstone_IoT2Kinesis_Rule_WS_03" {
  name        = "capstone_IoT2Kinesis_Rule_WS_03"
  enabled     = true
  sql         = "SELECT * FROM 'iot/ss' WHERE sprinkler_id = 'WS_03'"
  sql_version = "2016-03-23"

  kinesis {
    role_arn     = aws_iam_role.capstone_IoT2Kinesis_Role.arn
    stream_name  = aws_kinesis_stream.Agri_Water.name
    partition_key = "Sprinkler_03"
  }
}

resource "aws_iot_topic_rule" "capstone_IoT2Kinesis_Rule_WS_04" {
  name        = "capstone_IoT2Kinesis_Rule_WS_04"
  enabled     = true
  sql         = "SELECT * FROM 'iot/ss' WHERE sprinkler_id = 'WS_04'"
  sql_version = "2016-03-23"

  kinesis {
    role_arn     = aws_iam_role.capstone_IoT2Kinesis_Role.arn
    stream_name  = aws_kinesis_stream.Agri_Water.name
    partition_key = "Sprinkler_04"
  }
}

resource "aws_iot_topic_rule" "capstone_IoT2Kinesis_Rule_WS_05" {
  name        = "capstone_IoT2Kinesis_Rule_WS_05"
  enabled     = true
  sql         = "SELECT * FROM 'iot/ss' WHERE sprinkler_id = 'WS_05'"
  sql_version = "2016-03-23"

  kinesis {
    role_arn     = aws_iam_role.capstone_IoT2Kinesis_Role.arn
    stream_name  = aws_kinesis_stream.Agri_Water.name
    partition_key = "Sprinkler_05"
  }
}
# Create the IAM Role for IoT to Kinesis
resource "aws_iam_role" "capstone_IoT2Kinesis_Role" {
  name               = "capstone_IoT2Kinesis_Role"
  assume_role_policy = data.aws_iam_policy_document.iot_assume_role_policy.json
}

data "aws_iam_policy_document" "iot_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["iot.amazonaws.com"]
    }
  }
}

# Attach the required policies to the IoT to Kinesis Role
resource "aws_iam_role_policy" "capstone_IoT2Kinesis_Role_policy" {
  name   = "capstone_IoT2Kinesis_Role_policy"
  role   = aws_iam_role.capstone_IoT2Kinesis_Role.id
  policy = data.aws_iam_policy_document.capstone_IoT2Kinesis_Role_policy_doc.json
}

data "aws_iam_policy_document" "capstone_IoT2Kinesis_Role_policy_doc" {
  statement {
    effect    = "Allow"
    actions   = ["kinesis:PutRecord", "kinesis:PutRecords", "kinesis:*"]
    resources = ["arn:aws:kinesis:${var.aws_region}:${var.aws_account_id}:stream/${aws_kinesis_stream.Agri_Water.name}"]
  }

  statement {
    effect    = "Allow"
    actions   = ["iot:Publish", "iot:Subscribe", "iot:*"]
    resources = ["arn:aws:iot:${var.aws_region}:${var.aws_account_id}:topic/iot/ss"]
  }
}

# Create the Kinesis Stream
resource "aws_kinesis_stream" "Agri_Water" {
  name           = "Agri_Water"
  shard_count    = 1 # Adjust the shard count as needed
  stream_mode_details {
    stream_mode = "PROVISIONED"
  }
}

# Create the Lambda Function
resource "aws_lambda_function" "Sprinkler_Controller" {
  filename         = "lambda_function.zip" # Replace with the path to your Lambda function code
  function_name    = "Sprinkler_Controller"
  role             = aws_iam_role.lambda_kinesis_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = filebase64sha256("lambda_function.zip") # Replace with the hash of your Lambda function code
}

# Create the IAM Role for Lambda to access Kinesis
resource "aws_iam_role" "lambda_kinesis_role" {
  name               = "lambda_kinesis_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# Attach the Kinesis Stream Read Policy to the Lambda Role
resource "aws_iam_role_policy_attachment" "lambda_kinesis_read_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonKinesisReadOnlyAccess"
  role       = aws_iam_role.lambda_kinesis_role.name
}

# Attach the IoTFullAccess Policy to the Lambda Role
resource "aws_iam_role_policy_attachment" "lambda_iot_full_access_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AWSIoTFullAccess"
  role       = aws_iam_role.lambda_kinesis_role.name
}

resource "aws_cloudwatch_event_rule" "every_five_minutes" {
  name                = "every_five_minutes"
  schedule_expression = "rate(1 minutes)"
}

resource "aws_cloudwatch_event_target" "invoke_lambda" {
  rule      = aws_cloudwatch_event_rule.every_five_minutes.name
  target_id = "target_id"
  arn       = aws_lambda_function.Sprinkler_Controller.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_invoke_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.Sprinkler_Controller.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_five_minutes.arn
}

# # Create the IoT Rule for DynamoDB
# resource "aws_iot_topic_rule" "capstone_IoT2DynamoDB_Rule" {
#   name        = "capstone_IoT2DynamoDB_Rule"
#   enabled     = true
#   sql         = "SELECT * FROM 'iot/ss'"
#   sql_version = "2016-03-23"


#   dynamodb {
#   hash_key_field  = "sensor_id"
#   hash_key_value  = "${lookup(jsondecode(base64decode(topic_rule_payload.payload)), "sensor_id")}"
#   range_key_field = "timestamp"
#   role_arn        = aws_iam_role.capstone_IoT2DynamoDB_Role.arn
#   operation       = "INSERT"
#   payload_field   = "payload"
#   table_name      = aws_dynamodb_table.soil_data_table.name
#   }
# }

# # Create the IAM Role for IoT to DynamoDB
# resource "aws_iam_role" "capstone_IoT2DynamoDB_Role" {
#   name               = "capstone_IoT2DynamoDB_Role"
#   assume_role_policy = data.aws_iam_policy_document.iot_assume_role_policy.json
# }

# # Attach the required policies to the IoT to DynamoDB Role
# resource "aws_iam_role_policy" "capstone_IoT2DynamoDB_Role_policy" {
#   name   = "capstone_IoT2DynamoDB_Role_policy"
#   role   = aws_iam_role.capstone_IoT2DynamoDB_Role.id
#   policy = data.aws_iam_policy_document.capstone_IoT2DynamoDB_Role_policy_doc.json
# }

# data "aws_iam_policy_document" "capstone_IoT2DynamoDB_Role_policy_doc" {
#   statement {
#     effect = "Allow"
#     actions = [
#       "dynamodb:PutItem",
#       "dynamodb:UpdateItem",
#       "dynamodb:GetItem",
#       "dynamodb:Scan",
#       "dynamodb:Query",
#       "dynamodb:BatchWriteItem",
#       "dynamodb:DescribeTable",
#     ]
#     resources = ["${aws_dynamodb_table.soil_data_table.arn}"]
#   }

#   statement {
#     effect    = "Allow"
#     actions   = ["iot:Publish", "iot:Subscribe", "iot:*"]
#     resources = ["arn:aws:iot:${var.aws_region}:${var.aws_account_id}:topic/iot/ss"]
#   }
# }


# Create the DynamoDB Table
resource "aws_dynamodb_table" "soil_data_table" {
  name           = "soil_data_table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "sensor_id"
  range_key      = "timestamp"

  attribute {
    name = "sensor_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  # attribute {
  #   name = "sprinkler_id"
  #   type = "S"
  # }

  # attribute {
  #   name = "soil_temperature"
  #   type = "N"
  # }

  # attribute {
  #   name = "soil_humidity"
  #   type = "N"
  # }

  
}