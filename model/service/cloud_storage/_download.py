import os


def list_files(client, bucket):
    """
    Lists all the files in an AWS S3 bucket.

    Parameters
    ----------
    client : boto3.client
        The boto3 S3 client instance used to interact with AWS S3.
    bucket : str
        The name of the S3 bucket from which to list files.

    Returns
    -------
    list of str
        A list containing the keys (filenames) of all files stored in the specified S3 bucket.

    Notes
    -----
    This function uses the `list_objects` method of the boto3 S3 client to retrieve
    all objects in the specified bucket and then extracts the keys (names) of these
    objects to return a list of filenames.
    """

    files = []

    for key in client.list_objects(Bucket=bucket)['Contents']:
        files.append(key['Key'])

    return files


def download_file(client, bucket, local_dir, filename):
    """
    Downloads a file from an AWS S3 bucket to a specified local directory.

    Parameters
    ----------
    client : boto3.client
        The boto3 S3 client instance used to interact with AWS S3.
    bucket : str
        The name of the S3 bucket from which the file will be downloaded.
    local_dir : str
        The local directory path where the downloaded file will be saved.
    filename : str
        The name of the file to be downloaded from the S3 bucket.
    """
    abs_path = os.path.abspath(
        os.path.join(
            local_dir,
            filename
        )
    )

    client.download_file(bucket, filename, abs_path)
