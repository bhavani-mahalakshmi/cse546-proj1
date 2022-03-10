import os, base64
import time, json, traceback
from datetime import datetime, timezone
import requests

from s3 import ObjectStore
from face_recognition import face_match
from sqs import Queue
from credentials import INPUT_QUEUE

try:
  run_cont =  os.environ['RUN_CONTINUOUSLY']
except:
  print("Did not find RUN_CONTINUOUSLY environment variable. Defaulting to False.")
  run_cont = False

try: 
  shutdown_after = os.environ['SHUTDOWN_AFTER']
except:
  print("Did not find SHUTDOWN_AFTER environment variable. Defaulting to False.")
  shutdown_after = False


def process_image(image):
    """
    get image string from queue, store it in s3
    process it - store in local and classify
    output the answer to s3
    """
    file_name, image_string = image.split(";")
    temp_path = '/tmp/' + file_name
    # file_name = "test.jpg"
    with open(temp_path, "wb") as fh:
        fh.write(base64.b64decode(image_string))
    
    #Run classificaiton on image
    classification = face_match(temp_path, 'data.pt')
    # classification = "test"

    # Delete file
    os.remove(temp_path)

    output = [
                {
                    'Key': 'Image',
                    'Value': file_name
                },
                {
                    'Key': 'Classification',
                    'Value': classification
                },
                {
                    'Key': 'ClassifiedOn',
                    'Value': str(datetime.now(timezone.utc))
                }                               
            ]
    output = json.dumps(output)
    print(output)
    ObjectStore.upload_output_results(file_name, output)

def run_job():
  while Queue.get_num_messages_available(INPUT_QUEUE) > 0:
      try:
        print("Retrieving Image from SQS")
        image, receipt_handle = Queue.get_latest_message(INPUT_QUEUE)
        process_image(image)
        Queue.delete_message(INPUT_QUEUE, receipt_handle)
      except Exception:
        print("Error reading message")
        traceback.print_exc()
        time.sleep(2)


if run_cont: #Run forever
    while True:
        run_job()
        time.sleep(5) #poll every 5 seconds
else:
  run_job() #run once

if shutdown_after:
    print("Job Complete. Shutting Down")
    # ec2.stop_instances(InstanceIds=[instance_id])
else:
    print("Job Complete. Quitting...")

run_job()
