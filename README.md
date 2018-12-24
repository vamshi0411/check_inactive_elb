# check_inactive_elb
Lambda function to check instances on inactive elb 

# Requirments
IAM role with read only access for Route53 and Elasticloadbalacing is required for this lambda function. Optional Cloudwatch access is required if logs are forwarded to cloudwatch.

# Configure
Create a schedule CloudWatch rule to trigger this lambda function.
