import boto3

class AWSApiWrapper(object):
    PAGE_SIZE = 1000

    def __init__(self):
        self.session = self.create_aws_session()
        self.resource = self.create_s3_resource()

    def create_aws_session(self):
        return boto3.session.Session(profile_name='s3backups')

    def create_s3_resource(self):
        return self.session.resource('s3')

    def get_s3_bucket_by_name(self, bucket_name):
        return self.resource.Bucket(bucket_name)

    def get_s3_objects_by_bucket_name(self, bucket_name):
        bucket = self.get_s3_bucket_by_name(bucket_name)
        return bucket.objects.page_size(count=self.PAGE_SIZE)

    def copy(self, s3_object, bucket_name, new_key=None):
        copy_source = {
                'Bucket': s3_object.bucket_name,
                'Key': s3_object.key
                }
        dest_s3_key = new_key or s3_object.key
        dest = self.create_s3_object(bucket_name, dest_s3_key)
        return dest.copy_from(CopySource=copy_source)

    def create_s3_object(self, bucket_name, key):
        s3 = self.create_s3_resource()
        return s3.Object(bucket_name, key)

