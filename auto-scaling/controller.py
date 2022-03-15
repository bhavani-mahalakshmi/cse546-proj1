import ec2_manager as ec2_instance_manager
import time
import boto3

INPUT_QUEUE = "https://sqs.us-east-1.amazonaws.com/378107157540/Request-Queue.fifo"

WEB_TIER = "i-0d1247d2963d81ff8"

client = boto3.client(
                        'sqs',
                        region_name='us-east-1'
                    )

def auto_scale_instances():

    queue_length = int(client.get_queue_attributes(QueueUrl=INPUT_QUEUE,AttributeNames=['ApproximateNumberOfMessages']).get("Attributes").get("ApproximateNumberOfMessages"))

    print("Request queue length:", queue_length)

    # band_dict = {0: 0, 20: 1, 100: 2, 500: 5, 1000: 19}

    running_instances = ec2_instance_manager.get_running_instances()
    stopped_instances = ec2_instance_manager.get_stopped_instances()
    running_instances.remove(WEB_TIER)

    if queue_length == 0:
        # all_instances = ec2_instance_manager.get_running_instances()
        # all_instances.remove(WEB_TIER)
        # print("Queue is empty, shutting down all instances (downscaling)")
        # ec2_instance_manager.bulk_stop_instances(all_instances)
        return

    elif 1 <= queue_length <= 5:
        if len(running_instances) == 0:
            if len(stopped_instances) >= 1:
                ec2_instance_manager.start_instance(stopped_instances[0])
            else:
                ec2_instance_manager.create_instance()

    elif 5 < queue_length <= 50:
        if len(running_instances) < 10:
            length_of_running = len(running_instances)
            length_of_stopped = len(stopped_instances)
            needed_instances = 10 - length_of_running
            if length_of_stopped >= needed_instances:
                ec2_instance_manager.bulk_start_instances(stopped_instances[:needed_instances])
            else:
                ec2_instance_manager.bulk_start_instances(stopped_instances)
                for _ in range(needed_instances-length_of_stopped):
                    ec2_instance_manager.create_instance()

    else:
        if len(running_instances) < 19:
            length_of_running = len(running_instances)
            length_of_stopped = len(stopped_instances)
            needed_instances = 19 - length_of_running
            if length_of_stopped >= needed_instances:
                ec2_instance_manager.bulk_start_instances(stopped_instances[:needed_instances])
            else:
                ec2_instance_manager.bulk_start_instances(stopped_instances)
                for _ in range(needed_instances-length_of_stopped):
                    ec2_instance_manager.create_instance()

while True:
    print("Starting Auto Scaling")
    auto_scale_instances()
    time.sleep(5)