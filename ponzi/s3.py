import boto.s3.connection


class S3(object):

    def __init__(self, options):
        self.connection = boto.s3.connection.S3Connection(
            aws_access_key_id=options["aws_access_key"],
            aws_secret_access_key=options["aws_secret_key"]
        )
        self.bucket = self.connection.get_bucket(options["bucket_name"])

    def send_file(self, filename, key_name):
        print filename, key_name
        key = self.bucket.get_key(key_name)
        if not key:
            key = self.bucket.new_key(key_name)
        key.set_contents_from_filename(filename)
