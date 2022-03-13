import ec2_manager as ec2_instance_manager
import time
import boto3

INPUT_QUEUE = "https://sqs.us-east-1.amazonaws.com/051675418934/Input-Image-Queue.fifo"

WEB_TIER = "i-0e9c8fcb5f467994f"
APP_TIER = "i-0b41e866efe0c2b80"

def auto_scale_instances():
    client = boto3.client(
                            'sqs',
                            region_name='us-east-1'
                        )

    queue_length = int(client.get_queue_attributes(QueueUrl=INPUT_QUEUE,AttributeNames=['ApproximateNumberOfMessages']).get("Attributes").get("ApproximateNumberOfMessages"))

    print("Request queue length:", queue_length)

    if queue_length == 0:
        all_instances = ec2_instance_manager.get_running_instances()
        all_instances.remove(WEB_TIER)
        all_instances.remove(APP_TIER)
        print("Queue is empty, shutting down all instances (downscaling)")
        ec2_instance_manager.bulk_stop_instances(all_instances)
        return

    else:
        running_instances = ec2_instance_manager.get_running_instances()
        num_of_running_instances = len(running_instances)
        print("Running instances:", running_instances)
        if num_of_running_instances == 19:
            print("Im at max capacity")
            return
        
        if num_of_running_instances < queue_length:
            stopped_instances = ec2_instance_manager.get_stopped_instances()
            num_of_available_instances = len(stopped_instances)

            to_start = num_of_available_instances - queue_length
            if to_start > 0:
                instances_to_start = stopped_instances[:to_start]
            if to_start < 0:
                instances_to_start = stopped_instances
            ec2_instance_manager.bulk_start_instances(instances_to_start)
        else:
            #scale down
            #web tier
            pass
            # running_instances.remove(WEB_TIER)
            # #app tier
            # running_instances.remove(APP_TIER)
            # to_stop = len(running_instances) - queue_length
            # ec2_instance_manager.bulk_stop_instances(running_instances[:to_stop])

while True:
    print("Starting Auto Scaling")
    auto_scale_instances()
    time.sleep(30)