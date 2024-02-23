import logging
import os

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from dotenv import load_dotenv, find_dotenv

from model.service.cloud_storage._download import list_files, download_file
from model.service.cloud_storage._upload import upload_file

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


bucket = os.getenv('AWS_BUCKET')
s3 = boto3.client('s3')


def check_aws_config():
    """
    Validates the AWS S3 configuration by attempting to list objects in the specified bucket.

    Returns
    -------
    bool
        Returns True if the S3 bucket is accessible with the current configuration.
        Otherwise, logs a warning and returns False.

    Notes
    -----
    This function checks for two common issues:
    - The S3 bucket specified by the AWS_BUCKET environment variable does not exist or is not accessible.
    - The AWS credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) are not set or are incorrect.

    The function uses boto3's client to access S3, which will automatically use credentials
    set in the environment variables.
    """
    try:
        s3.list_objects(Bucket=bucket)
        return True
    except ClientError:
        logging.warning(f"Bucket {bucket} does not exist. AWS_BUCKET must be set.")
        return False
    except NoCredentialsError:
        logging.warning(f"The provided credentials are wrong. "
                        f"AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set.")


def upload_models(local_models_dir):
    """
    Uploads new machine learning models from a local directory to an AWS S3 bucket.

    Parameters
    ----------
    local_models_dir : str
        The directory containing the local model files to be uploaded.

    Notes
    -----
    This function identifies models that are present locally but not in the cloud,
    and uploads them to ensure that the S3 bucket is up-to-date. It leverages helper
    functions `list_files` for listing cloud files, `get_saved_models` for identifying
    local models, and `upload_file` for the upload process.
    """

    # Get list of files in the cloud
    cloud_files = set(list_files(s3, bucket))

    # Get list of local files
    local_files = set(get_saved_models(local_models_dir))

    # Compare both lists
    files_to_upload = local_files.difference(cloud_files)

    # Upload any new files
    if len(files_to_upload) > 0:
        for file in files_to_upload:
            upload_file(s3, bucket, local_models_dir, file)


def download_models(local_models_dir):
    """
    Downloads new machine learning models from an AWS S3 bucket to a local directory.

    Parameters
    ----------
    local_models_dir : str
        The local directory where the downloaded model files will be saved.

    Notes
    -----
    This function identifies models that are present in the cloud but not locally,
    and downloads them to ensure the local directory is up-to-date. It uses helper
    functions `list_files` to list cloud files, `get_saved_models` to identify local
    models, and `download_file` for the download process.

    It handles the synchronization by comparing the list of files in the cloud
    against the list of files locally, and only downloads those that are missing locally.
    """

    # Get list of files in the cloud
    cloud_files = set(list_files(s3, bucket))

    # Get list of local files
    local_files = set(get_saved_models(local_models_dir))

    # Compare both lists
    files_to_download = cloud_files.difference(local_files)

    # Upload any new files
    if len(files_to_download) > 0:
        for file in files_to_download:
            download_file(s3, bucket, local_models_dir, file)


def get_saved_models(local_models_dir):
    """
    Retrieves a list of saved machine learning model filenames from a specified local directory.

    Parameters
    ----------
    local_models_dir : str
        The local directory to search for saved model files.

    Returns
    -------
    list of str
        A list containing the filenames of all '.pkl' files found in the specified directory.

    Notes
    -----
    This function is primarily used to identify which models are currently saved locally,
    facilitating the synchronization process with the cloud storage by identifying which
    files need to be uploaded or downloaded.
    """
    all_files = [f for f in os.listdir(local_models_dir)
                 if os.path.isfile(os.path.join(local_models_dir, f))]

    models = [f for f in all_files if '.pkl' in f]

    return models
