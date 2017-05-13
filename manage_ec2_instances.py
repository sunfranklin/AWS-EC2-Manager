#
# Copyright (c) 2017, ScienceLogic, LLC
#
#
# This software is the copyrighted work of ScienceLogic, LLC.
#
# Use of the Software  is  governed  by  the  terms  of  the  software  license
# agreement, which accompanies or  is  included  with  the  Software  ("License
# Agreement").  An end user is not permitted to install any  Software  that  is
# accompanied by or includes a License Agreement, unless he or she first  agree
# to the License Agreement terms. The Software is made available solely for use
# by end users  according  to  the  License  Agreement.   Any  reproduction  or
# redistribution of the Software not in accordance with the  License  Agreement
# is expressly prohibited by law, and may result in severe civil  and  criminal
# penalties. Violators will be prosecuted to the maximum extent possible.
#
# WITHOUT LIMITING THE FOREGOING, COPYING OR REPRODUCTION OF  THE  SOFTWARE  TO
# ANY OTHER SERVER OR LOCATION FOR FURTHER REPRODUCTION  OR  REDISTRIBUTION  IS
# EXPRESSLY PROHIBITED.
#
# THE SOFTWARE IS WARRANTED, IF AT ALL, ONLY ACCORDING  TO  THE  TERMS  OF  THE
# LICENSE AGREEMENT. EXCEPT AS WARRANTED IN THE LICENSE AGREEMENT, SCIENCELOGIC
# LLC.  HEREBY DISCLAIMS ALL WARRANTIES  AND  CONDITIONS  WITH  REGARD  TO  THE
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES AND CONDITIONS OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT.
#
# Author: Frank Sun
#
# #############################################################################
#
# manage_ec2_instances.py
#
# #############################################################################
#
# Description:
#     This Python script starts and stops EC2 instances in an AWS account.
#     This script has a dependency on the boto3 and requests libraries..
#
# Syntax:
#     python manage_ec2_instances.py [aws_access_key_id]
#                                    [aws_secret_access_key] 
#                                    [start|stop]
#                                    [region]
#                                    [slack_webhook(optional)]
#                                    [instanceids(optional)]
# 
# Paramaters:
#     aws_access_key_id (string) --
#         [REQUIRED]
#         AWS access key
#     
#     aws_secret_access_key (string) --
#         [REQUIRED]
#         AWS secret key
#
#     action (string) --
#         [REQUIRED]
#         Determines whether the script starts or stops C2 instances.
#
#     region (string) --
#         [REQUIRED]
#         The region that will be affected.
#
#     slack_webhook (string) --
#         [optional]
#         The webhook that allows the script to post messages to Slack.
#         This is an optional parameter.
#         Default: If no webhook is provided, the script will not post
#                  messages to a Slack channel.
#
#     instance IDs (strings) --
#         [optional]
#         Specify one or more EC2 instance(s) to start or stop.
#         Default: If no EC2 instance IDs are provided, the script will
#                  start or stop all EC2 instances in the region.
#
# #############################################################################

try:
    import boto3, sys, requests, json
except ImportError, ie:
    print ie

def main_worker():
    aws_access_key_id = None
    aws_secret_access_key = None
    action = None
    region = None
    slack_webhook = None
    instance_id = None 
    aws_regions = []

    # Check the number of arguments we are providing the script
    if len(sys.argv) == 5:
        # No specific Instance ID was provided. 
        # All instances in a region will be started or stopped.
        aws_access_key_id = sys.argv[1]
        aws_secret_access_key = sys.argv[2]
        action = sys.argv[3]
        region = sys.argv[4]
    elif len(sys.argv) > 5:
        # Instance IDs were provided. All specified instances will be started or stopped.
        instance_id = []
        aws_access_key_id = sys.argv[1]
        aws_secret_access_key = sys.argv[2]
        action = sys.argv[3]
        region = sys.argv[4]
        if sys.argv[5].startswith("https://hooks.slack.com/services/"):
            slack_webhook = sys.argv[5]
            print "Using Slack webhook {}.".format(slack_webhook)
            for i in range(6,len(sys.argv)):
                instance_id.append(str(sys.argv[i]))
        else:
            for i in range(5,len(sys.argv)):
                instance_id.append(str(sys.argv[i]))
    else:
        # Invalid usage
        print "Expected Usage: python manage_ec2_instances.py [aws_access_key_id] [aws_secret_access_key] [start|stop] [region-name] [instanceid (optional)] \n"
        sys.exit(0)

    try:
        # Connect to AWS EC2 to get a list of all available Amazon regions
        conn = boto3.client('ec2',
                            region_name='us-east-1',
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key)
        if conn:
            region_response = conn.describe_regions()
            if region_response:
                regions_list = region_response.get('Regions')
                for regions in regions_list:
                    if 'RegionName' in regions:
                        aws_regions.append(regions['RegionName'])
    except Exception, exc:
        error = "Boto3 Connection Error: {}".format(exc)
        print error
        sys.exit(0)

    # Check region
    if not region or region.isspace():
        print "Region argument is missing. \n"
        sys.exit(0)
    elif not region in aws_regions:
        print "Invalid region provided. List of valid regions are {}. \n".format(aws_regions)
        sys.exit(0)

    # Check action
    if action == "start":
        start_or_stop_instances(aws_access_key_id, aws_secret_access_key, region, "start", slack_webhook, instance_id)
    elif action == "stop":
        start_or_stop_instances(aws_access_key_id, aws_secret_access_key, region, "stop", slack_webhook, instance_id)
    else:
        print "Invalid Action: '{0}'. The first argument should be either start or stop. \n".format(action)
        sys.exit(0)


def start_or_stop_instances(aws_access_key_id, aws_secret_access_key, region, action, slack_webhook=None, instance_id=None):
    try:
        # Connect to AWS EC2.
        conn = boto3.client('ec2',
                            region_name=region,
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key)
    except Exception, exc:
        error = "Boto3 Connection Error: {}".format(exc)
        print error
        sys.exit(0)
    try:
        if conn:
            if instance_id:
                # Start or stop specific instances
                print "Attempting to {} the EC2 Instance(s): {} ".format(action, instance_id)
                if action == "start":
                    # Start the list of instance(s)
                    start_resp = conn.start_instances(InstanceIds=instance_id)
                    msg = "Success: The following EC2 Instances have been started in region {}:\n{}".format(region, instance_id)
                    print msg
                    if slack_webhook:
                        slack_notifier(slack_webhook, msg)
                elif action == "stop":
                    # Stop the list of instance(s)
                    stop_resp = conn.stop_instances(InstanceIds=instance_id)
                    msg = "Success: The following EC2 Instances have been stopped in region {}:\n{}".format(region, instance_id)

                    print msg
                    if slack_webhook:
                        slack_notifier(slack_webhook, msg)
            else:
                # Start or stop all instances in the specified region
                print "Attempting to {} all EC2 instances in the region {}.".format(action, region)
                instances_to_stop = []
                instances_to_start = []
                all_instances = {}
                marker = None
                # Get all EC2 instances in the region to get status and ID.
                while True:
                    if marker is None:
                        desc_resp = conn.describe_instances(MaxResults=5)
                        all_instances = desc_resp
                    else:
                        desc_resp = conn.describe_instances(NextToken=marker)
                        next_resp = desc_resp.get('Reservations', None)
                        all_instances.get('Reservations').extend(next_resp)
                    # Check for a token in case of pagination
                    marker = desc_resp.get('NextToken', None)
                    if marker is None:
                        break
                reservations = all_instances.get('Reservations')
                for instances in reservations:
                    for instance in instances.get('Instances'):
                        if instance.get('State').get('Name') == "running":
                            instances_to_stop.append(instance.get('InstanceId'))
                        if instance.get('State').get('Name') == "stopped":
                            instances_to_start.append(instance.get('InstanceId'))
                
                if action == "start":
                    if instances_to_start:
                        # Start the list of instance(s)
                        print "EC2 instances to start: \n{}".format(instances_to_start)
                        start_resp = conn.start_instances(InstanceIds=instances_to_start)
                        msg = "Success: All EC2 Instances have been started in region {}.".format(region)
                        print msg
                        if slack_webhook:
                            slack_notifier(slack_webhook, msg)
                    else:
                        print "No instances to start in region {}.".format(region)
                elif action == "stop":
                    if instances_to_stop:
                        # Stop the list of instance(s)
                        print "EC2 instances to stop: \n{}".format(instances_to_stop)
                        stop_resp = conn.stop_instances(InstanceIds=instances_to_stop)
                        msg = "Success: All EC2 Instances have been stopped in region {}.".format(region)
                        print msg
                        if slack_webhook:
                            slack_notifier(slack_webhook, msg)
                    else:
                        print "No instances to stop in region {}.".format(region)

    except Exception, ei:
        error = "Exception: %s" % str(ei)
        print error
        #slack_notifier(error)
        sys.exit(0)

# Posts a message to the team-rebelscrum slack channel
def slack_notifier(slack_webhook, message):
    slack_data = {"text": message}
    response = requests.post(slack_webhook, 
                             data=json.dumps(slack_data),
                             headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        print "Error: Slack service not found. Verify Slack webhook."

main_worker()
