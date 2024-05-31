from flask import Flask, jsonify, render_template
import boto3
from boto3.dynamodb.conditions import Key
import datetime

app = Flask(__name__)

# DynamoDB client
dynamodb = boto3.resource('dynamodb')
sensor_table = dynamodb.Table('Soil_Sensor')
weather_table = dynamodb.Table('Weather')
sprinkler_table = dynamodb.Table('Sprinkler')
meta_data_table = dynamodb.Table('Meta_Data')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/data')
def get_data():
    # Get sensor data from DynamoDB
    sensor_response = sensor_table.scan()
    sensor_data = sensor_response['Items']

    # Get weather data from the last hour
    now = datetime.datetime.utcnow()
    one_hour_ago = now - datetime.timedelta(hours=1)
    weather_response = weather_table.query(
        KeyConditionExpression=Key('timestamp').gte(one_hour_ago.isoformat())
    )
    weather_data = weather_response['Items']

    # Get sprinkler data from DynamoDB
    sprinkler_response = sprinkler_table.scan()
    sprinkler_data = sprinkler_response['Items']

    return jsonify({
        'sensor_data': sensor_data,
        'weather_data': weather_data,
        'sprinkler_data': sprinkler_data,
        'metadata': meta_data_table
    })


if __name__ == '__main__':
    app.run(debug=True)
