# outputs.hcl

output "sensor_table_name" {
  description = "The name of the DynamoDB table for sensor data"
  value       = aws_dynamodb_table.sensor_table.name
}

output "sensor_table_arn" {
  description = "The ARN of the DynamoDB table for sensor data"
  value       = aws_dynamodb_table.sensor_table.arn
}

output "weather_table_name" {
  description = "The name of the DynamoDB table for weather data"
  value       = aws_dynamodb_table.weather_table.name
}

output "weather_table_arn" {
  description = "The ARN of the DynamoDB table for weather data"
  value       = aws_dynamodb_table.weather_table.arn
}

output "sprinkler_table_name" {
  description = "The name of the DynamoDB table for sprinkler data"
  value       = aws_dynamodb_table.sprinkler.name
}

output "sprinkler_table_arn" {
  description = "The ARN of the DynamoDB table for sprinkler data"
  value       = aws_dynamodb_table.sprinkler.arn
}