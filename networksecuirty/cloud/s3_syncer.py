import subprocess
import sys

from networksecuirty.exception.exception import NetworkSecurityException
class S3Sync:
    def sync_folder_to_s3(self,folder,aws_bucket_url):
        try:
            subprocess.run(
                ["aws", "s3", "sync", folder, aws_bucket_url],
                check=True,
            )
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
    def sync_folder_from_s3(self,folder,aws_bucket_url):
        try:
            subprocess.run(
                ["aws", "s3", "sync", aws_bucket_url, folder],
                check=True,
            )
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e

        