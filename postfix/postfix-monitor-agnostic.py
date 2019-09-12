#!/usr/bin/python3.6
# Requirements: boto3, requests
# This script monitorize postfix log, send 0 to AWS Cloudwatch if is working, either it sends 1
# Author: Iván Villa Sánchez <klaussius@hotmail.es>
#
# Comments and improvements always are welcome!
#

import time
import requests
import datetime
import os
import boto3

message = "Message in failure mail."
subject = "Subject in failure mail"
mail_from = "mail-from@email.com"
mail_to = "mail-to@email.com"
time_threshold = 60000

# Utils
def sendMail():
    """Send email using postfix"""
    command = "echo \"" + message + "\" | mailx -r " + mail_from + " -s \"" + subject + "\" " + mail_to
    os.system(command)

def monthToNum(shortMonth):
    """Convert month to num"""
    return{
        'Jan' : 1,
        'Feb' : 2,
        'Mar' : 3,
        'Apr' : 4,
        'May' : 5,
        'Jun' : 6,
        'Jul' : 7,
        'Aug' : 8,
        'Sep' : 9,
        'Oct' : 10,
        'Nov' : 11,
        'Dec' : 12
    }[shortMonth]

def last_log_date():
    """Get last log date, parse and return in epoch"""
    # Getting last log date
    log_ubication ="/var/log/mail.log"
    fileHandle = open(log_ubication, "r")
    lineList = fileHandle.readlines()
    fileHandle.close()
    last_line = lineList[len(lineList)-1]
    parts = last_line.split(" ")
    # Using current year as log year, because there is no year data in the log
    now = datetime.datetime.now()
    year = int(now.year)
    month = int(monthToNum(parts[0]))
    day = int(parts[1])
    hour = int(parts[2].split(":")[0])
    minute = int(parts[2].split(":")[1])
    second = int(parts[2].split(":")[2])
    event_date = datetime.datetime(year, month, day, hour, minute, second)
    return event_date.strftime('%s')

def send_notification_aws(value):
    """Send notification to AWS Cloudwatch"""
    url_credentials = "http://169.254.169.254/latest/meta-data/iam/security-credentials/atCloudWatchRole"
    url_instance_id = "http://169.254.169.254/latest/meta-data/instance-id"
    json = requests.get(url_credentials).json()
    instance_id = requests.get(url_instance_id).text
    region = 'eu-west-1'
    AK = json['AccessKeyId']
    SK = json['SecretAccessKey']
    ST = json['Token']
    cloudwatch = boto3.client(
            'cloudwatch',
            aws_access_key_id=AK,
            aws_secret_access_key=SK,
            aws_session_token=ST,
            region_name=region
            )
    cloudwatch.put_metric_data(
        MetricData=[
            {
                'MetricName': 'Postfix',
                'Dimensions': [
                    {
                        'Name': 'Value',
                        'Value': instance_id
                    },
                ],
                'Unit': 'None',
                'Value': value
            },
        ],
        Namespace='POSTFIX'
    )
    if value == 0:
        print("Todo ok - diff: " + str(time_diff))
    else:
        print("Todo mal - diff: " + str(time_diff))

time_diff = time.time() - float(last_log_date())
if time_diff > time_threshold:
    sendMail()
    time.sleep(15)
    time_diff = time.time() - float(last_log_date())
    if time_diff > time_threshold:
        send_notification_aws(1)
    else:
        send_notification_aws(0)
else:
    send_notification_aws(0)