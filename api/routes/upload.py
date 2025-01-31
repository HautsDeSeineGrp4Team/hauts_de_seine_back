import os

from fastapi import UploadFile, File, APIRouter, HTTPException
from dotenv import load_dotenv

from minio import Minio
from minio.error import S3Error


load_dotenv()
router = APIRouter()

@router.post("/upload/img")
async def create_upload_file(file: UploadFile = File(...)):

    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        raise HTTPException(status_code=500, detail='Something went wrong')
    finally:
        file.file.close()


    # and secret key.
    client = Minio("minio.cloud.decaweb.fr",
        access_key=os.getenv('S3_KEYNAME'),
        secret_key=os.getenv("S3_SECRETKEY"),
    )

    # The destination bucket and filename on the MinIO server
    bucket_name = "pcc-staging"
    destination_file = file.filename

    # Make the bucket if it doesn't exist.
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    # Upload the file, renaming it in the process
    client.fput_object(
        bucket_name, destination_file, file.filename,
    )
    try:
        os.remove(file.filename)
    except: 
        pass

    return {"filename": "minio.cloud.decaweb.fr/" + "pcc-staging/" + file.filename}

