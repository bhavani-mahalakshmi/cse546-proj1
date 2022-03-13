import os, base64
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
    file_name = image["file_name"]
    image_string = image["encoded_image"]
    unique_id = image["unique_id"]
    temp_path = '/tmp/' + file_name
    with open(temp_path, "wb") as fh:
        fh.write(base64.b64decode(image_string))

    #Run classificaiton on image
    classification = face_match(temp_path, 'data.pt')

    print("Done: ", file_name, classification)
    key = file_name.split(".")[0]
    value = classification[0]
    
    response_message = {
      "unique_id": unique_id,
      "classification": value
    }
    response_message = json.dumps(response_message)
    Queue.send_message(OUTPUT_QUEUE, response_message, unique_id)
    print("Result sent to output queue")

    ObjectStore.upload_input_images(temp_path)
    print("Input image file uploaded to s3")

    ObjectStore.upload_output_results(key, value)
    print("Output stored in s3")
    
    # Delete file
    os.remove(temp_path)

def run_job():
  if Queue.get_num_messages_available(INPUT_QUEUE) > 0:
      try:
        print("Retrieving Image from SQS")
        image_request, receipt_handle = Queue.get_latest_message(INPUT_QUEUE)
        image_request = json.loads(image_request)
        process_image(image_request)
        Queue.delete_message(INPUT_QUEUE, receipt_handle)
      except Exception:
        print("Error reading message")
        traceback.print_exc()
  else:
    print("No more messages in queue")
    if not run_cont:
      import requests
      r = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
      instance_id = r.text
      print("Stopping instance ", instance_id)
      time.sleep(120)
      if Queue.get_num_messages_available(INPUT_QUEUE) > 0:
        return
      else:
        os.system('sudo shutdown now -h')
      # boto3.client('ec2').stop_instances(
      #         InstanceIds=[
      #             instance_id
      #         ],
      #         Hibernate=True|False,
      #         DryRun=True|False,
      #         Force=True|False
      #     )

while True:
    run_job()
