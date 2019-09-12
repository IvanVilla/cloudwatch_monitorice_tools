# Note
Requirements: boto3, requests.
The EC2 must have permission to send metrics to AWS Cloudwatch.
This script monitorize postfix log, send 0 to AWS Cloudwatch if is working, either it sends 1
