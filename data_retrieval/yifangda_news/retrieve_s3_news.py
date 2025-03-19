import boto3
from botocore.client import Config


# S3 configs
test_db_config = {
    'endpoint_url': "https://s3yw1kf1.efundsdemo.com:10443",
    'access_key': "OYHE04KP8EI3SCM1GGDD",
    'secret_key': "q8DYhzngkRoUIuIzXNN5eMYgWFedg8ZBjHBgAn2g",
    'bucket_name': "nsdc",
}
prod_db_config = {
    'endpoint_url': "https://s3yw1kf1.efundsdemo.com:10443",
    'access_key': "OYHE04KP8EI3SCM1GGDD",
    'secret_key': "q8DYhzngkRoUIuIzXNN5eMYgWFedg8ZBjHBgAn2g",
    'bucket_name': "nsdc",
}


def download_news_from_s3(news_code, local_filename=None, prod_env=False):
    """
    Download a file from a custom S3-compatible storage.

    :param news_code: News code.
    :param local_filename: The local file path to save the downloaded file.
    :param prod_env: if True use prod env.
    """
    if not prod_env:
        endpoint_url = test_db_config['endpoint_url']
        access_key = test_db_config['access_key']
        secret_key = test_db_config['secret_key']
        bucket_name = test_db_config['bucket_name']
        s3_key_template = "hermes/v1/newsbody/{}"
    else:
        endpoint_url = prod_db_config['endpoint_url']
        access_key = prod_db_config['access_key']
        secret_key = prod_db_config['secret_key']
        bucket_name = prod_db_config['bucket_name']
        s3_key_template = "hermes/v1/newsbody/{}"

    # Create an S3 client with a custom endpoint
    s3_key = s3_key_template.format(news_code)
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
    )

    try:
        if local_filename:
            s3.download_file(bucket_name, s3_key, local_filename)
        response = s3.get_object(Bucket=bucket_name, Key=s3_key)
        return response["Body"].read().decode("utf-8")  # Convert bytes to string
    except Exception as e:
        print(f"X Error downloading file: {e}")
        return "No news content found"


if __name__ == '__main__':
    news_code = "HEMOLDr0K6tyv9fweprV7Q"  # First news code
    news_code = "fxkYEVgZ3L-H0G1ZT6tJSQ"  # Second news code
    print(download_news_from_s3(news_code))
