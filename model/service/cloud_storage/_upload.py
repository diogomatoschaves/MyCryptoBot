import os


def upload_file(client, bucket, local_dir, filename):
    """
    Uploads a file to an AWS S3 bucket from a specified local directory.

    Parameters
    ----------
    client : boto3.client
        The boto3 S3 client instance used to interact with AWS S3.
    bucket : str
        The name of the S3 bucket to which the file will be uploaded.
    local_dir : str
        The local directory path from where the file will be uploaded.
    filename : str
        The name of the file to be uploaded to the S3 bucket.
    """

    abs_path = os.path.abspath(
        os.path.join(
            local_dir,
            filename
        )
    )

    with open(abs_path, "rb") as f:
        client.upload_fileobj(f, bucket, filename)
