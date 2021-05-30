import boto3
import os
import logging
import uuid
from webdriver_screenshot import WebDriverScreenshot

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
 
    screenshot_file = "{}-{}".format(''.join(filter(str.isalpha, os.environ['URL'])), str(uuid.uuid4()))
    driver = WebDriverScreenshot()

    logger.info('Fill the form and save screenshot')
    driver.save_screenshot(os.environ['URL'], os.environ['Email'], os.environ['Pwd'], '/tmp/{}-final.png'.format(screenshot_file))

    driver.close()

    if all (k in os.environ for k in ('BUCKET','DESTPATH')):
        ## Upload generated screenshot files to S3 bucket.
        s3.upload_file('/tmp/{}-final.png'.format(screenshot_file), 
                    os.environ['BUCKET'], 
                    '{}/{}-final.png'.format(os.environ['DESTPATH'], screenshot_file))