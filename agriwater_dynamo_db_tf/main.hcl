provider "aws" {
  region = "us-east-1"
}

resource "aws_dynamodb_table" "Soil_Sensor" {
  name           = "Soil_Sensor"
  hash_key       = "deviceID"
  range_key      = "Timestamp"

  attribute {
    name = "deviceID"
    type = "S"
  }

  attribute {
    name = "Timestamp"
    type = "N"
  }

  attribute {
    name = "Soil_temp"
    type = "N"
  }

  attribute {
    name = "soil_humidity"
    type = "N"
  }

  attribute {
    name = "device_latitude"
    type = "N"
  }

  attribute {
    name = "device_longitude"
    type = "N"
  }

  tags = {
    Name = "sensor_table"
    Environment = "dev"
  }
}

resource "aws_dynamodb_table" "weather_table" {
  name           = "weather_table"
  hash_key       = "OrderID"

  attribute {
    name = "OrderID"
    type = "S"
  }

  attribute {
    name = "ref_time"
    type = "N"
  }

  attribute {
    name = "sset_time"
    type = "N"
  }

  attribute {
    name = "srise_time"
    type = "N"
  }

  attribute {
    name = "clouds"
    type = "N"
  }

  attribute {
    name = "rain"
    type = "M"
  }

  attribute {
    name = "snow"
    type = "M"
  }

  attribute {
    name = "wnd"
    type = "M"
  }

  attribute {
    name = "humidity"
    type = "N"
  }

  attribute {
    name = "pressure"
    type = "M"
  }

  attribute {
    name = "temp"
    type = "M"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "detailed_status"
    type = "S"
  }

  attribute {
    name = "weather_code"
    type = "N"
  }

  attribute {
    name = "weather_icon_name"
    type = "S"
  }

  attribute {
    name = "visibility_distance"
    type = "N"
  }

  attribute {
    name = "dewpoint"
    type = "N"
  }

  attribute {
    name = "humidex"
    type = "N"
  }

  attribute {
    name = "heat_index"
    type = "N"
  }

  attribute {
    name = "utc_offset"
    type = "N"
  }

  attribute {
    name = "uvi"
    type = "N"
  }

  attribute {
    name = "precipitation_probability"
    type = "N"
  }

  tags = {
    Name = "weather_table"
    Environment = "dev"
  }
}

resource "aws_dynamodb_table" "Sprinkler" {
  name           = "Sprinkler"
  hash_key       = "deviceID"

  attribute {
    name = "deviceID"
    type = "S"
  }

  attribute {
    name = "Timestamp"
    type = "N"
  }

  attribute {
    name = "sprinkler_on"
    type = "BOOL"
  }

  attribute {
    name = "device_latitude"
    type = "N"
  }

  attribute {
    name = "device_longitude"
    type = "N"
  }

  tags = {
    Name = "sprinkler"
    Environment = "dev"
  }
}
