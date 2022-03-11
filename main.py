import os, base64, boto3
import time, json, traceback
from datetime import datetime, timezone
from s3 import ObjectStore
from face_recognition import face_match
from sqs import Queue
from credentials import INPUT_QUEUE, OUTPUT_QUEUE

try:
  run_cont =  bool(os.environ['RUN_CONTINUOUSLY'])
except:
  print("Did not find RUN_CONTINUOUSLY environment variable. Defaulting to False.")
  run_cont = False

def process_image(image):
    """
    get image string from queue, store it in s3
    process it - store in local and classify
    output the answer to s3
    """
    # file_name = "test.jpg"
    # classification = "test"

    file_name, image_string = image.split(";")
    temp_path = '/tmp/' + file_name
    with open(temp_path, "wb") as fh:
        fh.write(base64.b64decode(image_string))
    
    #Run classificaiton on image
    classification = face_match(temp_path, 'data.pt')

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
    key = file_name.split(".")[0]
    value = classification[0]
    ObjectStore.upload_output_results(key, value)
    Queue.send_message(OUTPUT_QUEUE, key+":"+value)
    
def run_job():
  if Queue.get_num_messages_available(INPUT_QUEUE) > 0:
      try:
        print("Retrieving Image from SQS")
        image, receipt_handle = Queue.get_latest_message(INPUT_QUEUE)
        process_image(image)
        Queue.delete_message(INPUT_QUEUE, receipt_handle)
      except Exception:
        print("Error reading message")
        traceback.print_exc()
        time.sleep(2)
  else:
    print("No more messages in queue")
    if os.getenv("ENV") == "production" and not run_cont:
      import requests
      r = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
      instance_id = r.text
      print("Stopping instance ", instance_id)
      boto3.client('ec2').stop_instances(
              InstanceIds=[
                  instance_id
              ],
              Hibernate=True|False,
              DryRun=True|False,
              Force=True|False
          )

while True:
    run_job()
    time.sleep(5) #poll every 5 seconds
