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
#     This script has a dependency on the boto3 library.
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
