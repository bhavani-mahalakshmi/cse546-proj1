import queue
import ec2_manager as ec2_instance_manager
import time
import boto3

INPUT_QUEUE = "https://sqs.us-east-1.amazonaws.com/051675418934/Input-Image-Queue.fifo"

WEB_TIER = "i-0e9c8fcb5f467994f"

def auto_scale_instances():
    client = boto3.client(
                            'sqs',
                            region_name='us-east-1'
                        )

    queue_length = int(client.get_queue_attributes(QueueUrl=INPUT_QUEUE,AttributeNames=['ApproximateNumberOfMessages']).get("Attributes").get("ApproximateNumberOfMessages"))

    print("Request queue length:", queue_length)

    # band_dict = {0: 0, 20: 1, 100: 2, 500: 5, 1000: 19}

    if queue_length == 0:
        all_instances = ec2_instance_manager.get_running_instances()
        all_instances.remove(WEB_TIER)
        print("Queue is empty, shutting down all instances (downscaling)")
        ec2_instance_manager.bulk_stop_instances(all_instances)
        return

    elif 1 <= queue_length <= 20:
        running_instances = ec2_instance_manager.get_running_instances()
        stopped_instances = ec2_instance_manager.get_stopped_instances()
        running_instances.remove(WEB_TIER)
        if len(running_instances) == 0:
            if len(stopped_instances) >= 1:
                ec2_instance_manager.start_instance(stopped_instances[0])
            else:
                ec2_instance_manager.create_instance()

    elif 20 < queue_length <= 100:
        running_instances = ec2_instance_manager.get_running_instances()
        stopped_instances = ec2_instance_manager.get_stopped_instances()
        running_instances.remove(WEB_TIER)
        if len(running_instances) < 2:
            length_of_running = len(running_instances)
            length_of_stopped = len(stopped_instances)
            needed_instances = 2 - length_of_running
            if length_of_stopped >= needed_instances:
                ec2_instance_manager.bulk_start_instances(stopped_instances[:needed_instances])
            else:
                for _ in range(needed_instances):
                    ec2_instance_manager.create_instance()

    elif 100 < queue_length <= 500:
        running_instances = ec2_instance_manager.get_running_instances()
        stopped_instances = ec2_instance_manager.get_stopped_instances()
        running_instances.remove(WEB_TIER)
        if len(running_instances) < 5:
            length_of_running = len(running_instances)
            length_of_stopped = len(stopped_instances)
            needed_instances = 5 - length_of_running
            if length_of_stopped >= needed_instances:
                ec2_instance_manager.bulk_start_instances(stopped_instances[:needed_instances])
            else:
                for _ in range(needed_instances):
                    ec2_instance_manager.create_instance()

    else:
        running_instances = ec2_instance_manager.get_running_instances()
        stopped_instances = ec2_instance_manager.get_stopped_instances()
        running_instances.remove(WEB_TIER)
        if len(running_instances) < 19:
            length_of_running = len(running_instances)
            length_of_stopped = len(stopped_instances)
            needed_instances = 19 - length_of_running
            if length_of_stopped >= needed_instances:
                ec2_instance_manager.bulk_start_instances(stopped_instances[:needed_instances])
            else:
                for _ in range(needed_instances):
                    ec2_instance_manager.create_instance()

        # running_instances = ec2_instance_manager.get_running_instances()
        # running_instances.remove(WEB_TIER)
        # num_of_running_instances = len(running_instances)
        # if num_of_running_instances == 19:
        #     print("Maximum capacity reached")
        #     return

        # if num_of_running_instances == 0:
            
        
        # if num_of_running_instances < queue_length:
        #     stopped_instances = ec2_instance_manager.get_stopped_instances()
        #     num_of_available_instances = len(stopped_instances)

        #     to_start = num_of_available_instances - queue_length
        #     if to_start > 0:
        #         instances_to_start = stopped_instances[:to_start]
        #     if to_start < 0:
        #         instances_to_start = stopped_instances
        #     ec2_instance_manager.bulk_start_instances(instances_to_start)
        # else:
        #     #scale down
        #     #web tier
        #     # running_instances.remove(WEB_TIER)
        #     # to_stop = len(running_instances) - queue_length
        #     # ec2_instance_manager.bulk_stop_instances(running_instances[:to_stop])
        #     pass

while True:
    print("Starting Auto Scaling")
    auto_scale_instances()
    time.sleep(30)