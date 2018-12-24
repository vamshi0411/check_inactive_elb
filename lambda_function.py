import boto3
import re
import json
from botocore.vendored import requests

elastic_load_balancer = boto3.client('elb')
route53 = boto3.client('route53')

def list_resource_recordsets():
    return (route53.list_resource_record_sets(HostedZoneId='<>'))

def check_prod_and_region(recordset):
    return (re.search("stage", recordset) and re.search("example", recordset))

def elb_name(Aname_value):
    if "-elb-xb-" in Aname_value:
        elb_name_pattern = "-elb-xb"
    elif "-elb-xa-" in Aname_value:
        elb_name_pattern = "-elb-xa"
    elif "-elb-ib-" in Aname_value:
        elb_name_pattern = "-elb-ib"
    elif "-elb-ia-" in Aname_value:
        elb_name_pattern = "-elb-ia"
    elif "-elb-b-" in Aname_value:
        elb_name_pattern = "-elb-b"
    else:
        elb_name_pattern = "-elb-a"

    if Aname_value.startswith( "internal"):
        lb_temp = Aname_value[9:]
        remove = lb_temp.split(elb_name_pattern,1)[1]
        return (lb_temp[:lb_temp.find(remove)])
    else:
        remove = Aname_value.split(elb_name_pattern,1)[1]
        return (Aname_value[:Aname_value.find(remove)])



def send_status_to_hipchat(message,color):
    room_id_real = "7119"
    auth_token_real = ""
    url = ''
    headers = {
        "content-type": "application/json",
        "authorization": "Bearer %s" % auth_token_real}
    datastr = json.dumps({
        'message': message,
        'color': color,
        'message_format': 'text',
        'notify': False,
        'from': 'Lambda'})
    request = requests.post(url, headers=headers, data=datastr)
    print (request.ok, request.status_code, request.text)
    return request.status_code

def all_elbs_scaled_down():
    send_status_to_hipchat("All inactive asgs scaled down","green")



def lambda_handler(event, context):
    count = 0
    
    # Get resource records list
    resource_record_set_list = list_resource_recordsets()

    # Converting to list
    ResourceRecordSets = resource_record_set_list.get("ResourceRecordSets")

    # Get each record set
    for itemi in ResourceRecordSets:
        resourcerecord = (itemi['Name'])

        # Check if resource record set is for prod and desired region
        if check_prod_and_region(resourcerecord):

            # Get Aname if traffic on recordset is zero
            if (itemi['Weight']) == 0:
                Aname = (itemi['ResourceRecords'])

                for itemj in Aname:
                    Aname_value = (itemj['Value'])

                    # Get elb name from Aname
                    lb = elb_name(Aname_value)


                    response_lb = elastic_load_balancer.describe_load_balancers(LoadBalancerNames=[lb])
                    lbname =  response_lb.get("LoadBalancerDescriptions")
                    for itemk in lbname:
                        instances = (itemk['Instances'])
                    if not instances:
                        print ("for " + lb + " no instances")
                    else:
                        print (lb + " instances not scaled down")
                        count += 1
                        send_status_to_hipchat(lb + " instances not scaled down","red")

    if count == 0:
        all_elbs_scaled_down()
