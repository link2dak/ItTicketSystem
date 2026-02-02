from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.environ["AZURE_CLIENT_ID"]
tenant_id = os.environ["AZURE_TENANT_ID"]
account_url = os.environ["AZURE_STORAGE_URL"]


#gets default credentials in order to get account info
credentials = DefaultAzureCredential()

#uploads a blob to a container
def upload_blob_data():
    container_name = 'blobcontainer'
    local_dir= 'input'

    #gets the storage account holding the container
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credentials)
    #gets container information
    container_client = blob_service_client.get_container_client(container = container_name)

    #name of files to upload
    filenames = os.listdir(local_dir)


    for filename in filenames:
        full_file_path = os.path.join(local_dir, filename)

        with open(full_file_path, "r") as f1:
            data = f1.read()
            container_client.upload_blob(name = filename, data = data)
def get_all_blob_data():
    container_name = 'blobcontainer'

    blob_service_client = BlobServiceClient(account_url = account_url, credential=credentials)
    container_client = blob_service_client.get_container_client(container = container_name)

    #loop through container and list them all and show the contents
    for blob in container_client.list_blobs():
        #gets the useable client
        blob_client = container_client.get_blob_client(blob= blob.name)

        #gets the data inside blob
        data = blob_client.download_blob().readall()
        print("blob name: " + blob.name + "\n")

        print("contents: " + data.decode("utf-8"))

if __name__ == '__main__':
    get_all_blob_data()