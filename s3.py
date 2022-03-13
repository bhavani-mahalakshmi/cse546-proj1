import os, boto3, traceback
from botocore.exceptions import NoCredentialsError
from credentials import INPUT_BUCKET, OUTPUT_BUCKET

class S3:
    obj = None
    def __init__(self) -> None:
        try:
            S3.obj = boto3.resource(
                                        's3',
                                        region_name='us-east-1'
                                    )                
        except NoCredentialsError:
            print("Credentials not available")
            return False

    def upload_file(self, bucket, file_name, key_name):
        try:
            S3.obj.Bucket(bucket).upload_file(file_name, key_name)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False

    def upload_result(self, bucket, key, value):
        try:
            S3.obj.Object(bucket, key).put(Body=value)
            print("Upload Successful")
            return True
        except Exception:
            traceback.print_exc()
            print("cant upload data")
            return False
    
    def download_file(self, bucket, key):
        local_file_path = "/Users/bhavani/Desktop/sem2/cc-proj1/bhavani-app-tier/input-images/downloaded/"
        if not os.path.exists(local_file_path):
            os.makedirs(local_file_path)
        S3.obj.Bucket(bucket).download_file(key, local_file_path+key)

    def retrieve_value(self, bucket, key):
        obj = S3.obj.Object(bucket, key)
        return obj.get()['Body'].read().decode('utf-8') 

class ObjectStore:
    s3 = S3()

    def __init__(self) -> None:
        pass

    @staticmethod
    def upload_input_images(location):
        """
        :param str location: location to the file on the local filesystem
        """   
        key = location.split('/')[-1]
        return ObjectStore.s3.upload_file(INPUT_BUCKET, location, key)

    @staticmethod
    def upload_output_results(file_name, result):
        """
        :param str file_name: file name of the input image
        :param str result: result from the DL model
        """   
        key = file_name.split(".")[0]
        return ObjectStore.s3.upload_result(OUTPUT_BUCKET, key, result)

def test():
    # ObjectStore.upload_input_images("/Users/bhavani/Desktop/sem2/cc-proj1/bhavani-app-tier/input-images/test.jpg")
    # ObjectStore.upload_output_results("test.jpg", "test1")
    # S3().download_file(INPUT_BUCKET, "test.jpg")
    print(S3().retrieve_value(OUTPUT_BUCKET, "testkey"))
    pass

# test()