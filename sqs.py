import boto3, json
from botocore.exceptions import NoCredentialsError
from credentials import ACCESS_KEY_ID, SECRET_ACCESS_KEY

class SQS:
    obj = None
    def __init__(self) -> None:
        try:
            SQS.obj = boto3.client(
                                        'sqs',
                                        region_name='us-east-1',
                                        aws_access_key_id=ACCESS_KEY_ID,
                                        aws_secret_access_key=SECRET_ACCESS_KEY
                                    )
        except NoCredentialsError:
            print("Credentials not available")
            return False

    def create_queue(self, name):
        return SQS.obj.create_queue(QueueName=name, Attributes={'DelaySeconds': '5'})

    def get_queue_by_name(self, name):
        return SQS.obj.get_queue_by_name(QueueName=name)

    def send_message(self, queue_url, message):
        SQS.obj.send_message(QueueUrl=queue_url,MessageBody=message, MessageGroupId='messageGroup1')

    def get_queue_attributes(self, queue_url, attributes):
        return SQS.obj.get_queue_attributes(QueueUrl=queue_url,AttributeNames=attributes)

    def get_latest_message(self, queue_url):
        """ Gets the first available message in queue """
        response = SQS.obj.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            VisibilityTimeout=10,
            WaitTimeSeconds=0
            )
        return response

    def delete_message(self, queue_url, receipt_handle):
        SQS.obj.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
            )


class Queue:
    sqs = SQS()

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_num_messages_available(queue_url):
        """ Returns the number of messages in the queue """
        response = Queue.sqs.get_queue_attributes(queue_url, ['ApproximateNumberOfMessages'])
        messages_available = response['Attributes']['ApproximateNumberOfMessages']
        return int(messages_available)

    @staticmethod
    def get_num_message_not_visible(queue_url):
        """ Returns the number of messages not visible in the queue """
        response = Queue.sqs.get_queue_attributes(queue_url, ['ApproximateNumberOfMessagesNotVisible'])
        messages_not_visible = response['Attributes']['ApproximateNumberOfMessagesNotVisible']
        return int(messages_not_visible)

    @staticmethod
    def get_latest_message(queue_url):
        """ Gets the first available message in queue """
        response = Queue.sqs.get_latest_message(queue_url)
        if "Messages" not in response:
            print("Queue is empty")
            return None
        receipt_handle = response['Messages'][0]['ReceiptHandle']
        print(type(receipt_handle))
        result = response['Messages'][0]['Body']
        return result, receipt_handle

    @staticmethod
    def delete_message(queue_url, receipt_handle):
        Queue.sqs.delete_message(queue_url, receipt_handle)

    @staticmethod
    def send_message(queue_url, message):
        Queue.sqs.send_message(queue_url, message)


# def test():
#     # print(Queue.send_message(INPUT_QUEUE, "hello"))
#     # res, h = (Queue.get_latest_message(INPUT_QUEUE))
#     # print(Queue.delete_message(INPUT_QUEUE, h))
#     # print(Queue.get_num_message_not_visible(INPUT_QUEUE))
#     # print(Queue.get_num_messages_available(INPUT_QUEUE))
#     pass
# test()
