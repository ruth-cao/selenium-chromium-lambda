import boto3
import os
import logging
import uuid
from webdriver_screenshot import WebDriverScreenshot

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
 
    url = os.environ['URL']
    screenshot_file = "{}-{}".format(''.join(filter(str.isalpha, url)), str(uuid.uuid4()))
    driver = WebDriverScreenshot()

    logger.info('Fill the form and save screenshot')
    email = get_parameter('/screenshot/email')
    pwd = get_parameter('/screenshot/pwd')
    result = driver.save_screenshot(url, email, pwd, '/tmp/{}-final.png'.format(screenshot_file))
     
    driver.close()

    s3 = boto3.client('s3')
    if all (k in os.environ for k in ('BUCKET','DESTPATH')):
        ## Upload generated screenshot files to S3 bucket.
        s3.upload_file('/tmp/{}-final.png'.format(screenshot_file), 
                    os.environ['BUCKET'], 
                    '{}/{}-final.png'.format(os.environ['DESTPATH'], screenshot_file))

    sns = boto3.client('sns')
    topicArn = get_parameter('topicArn')
    sns.publish(
          TopicArn=topicArn,
          Message='the result code is {0}'.format(result),
          Subject='The daily form filling is completed')

def get_parameter(name):
    ssm = boto3.client('ssm')
    parameter = ssm.get_parameter(Name=name, WithDecryption=True)
    return parameter['Parameter']['Value']