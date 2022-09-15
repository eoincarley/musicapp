DEFAULT_ARGS = {
    'owner': 'Airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 13),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('create_date_dimension', default_args=DEFAULT_ARGS,
          schedule_interval="@once")


def minio_add_bucket(ds, **kwargs):
    '''
    Add a bucket to Minio if one doesn't already exist.
    '''
    #--------------------------------------------------------#
    #    Define bucket, Minio endpoint. Setup Minio client
    #
    bucket_name = 'songs'
    minio_port = ':9000'
    minio_service = 'minio-service'
    minio_endpoint = ''.join((minio_service, minio_port))
    minio_client = get_minio_client('testkey', 'secretkey', 
                                    minio_endpoint=minio_endpoint)

    #---------------------------------------------------#
    #    Create a bucket if not already created.
    #
    try:
        if (not minio_client.bucket_exists(bucket_name)):
            minio_client.make_bucket(bucket_name)
        else:
            print('Bucket \'%s\' already exists' %(bucket_name))
    except S3Error as exc:
        print("Error occurred during bucket query/creation:", exc)

# Create a task to call your processing function
t1 = PythonOperator(
    task_id='generate_and_upload_to_s3',
    provide_context=True,
    python_callable=write_text_file,
    dag=dag
)