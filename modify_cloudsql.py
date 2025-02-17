import pandas as pd
from googleapiclient.discovery import build
from google.auth import default

def modify_cloudsql_instance(project_id, instance_name, cpu=None, memory=None):
    creds, _ = default()  # use default credentials saved while setting up gcloud CLI
    service = build('sqladmin', 'v1', credentials=creds)  # creates a cloud sql admin object

    instance = service.instances().get(project=project_id, instance=instance_name).execute() # Fetch the current instance settings

    # Prepare update request body
    update_body = {'settings': instance['settings']}
    update_mask = []

    if cpu and memory:
        update_body['settings']['tier'] = f"db-custom-{cpu}-{memory * 1024}"
        update_mask.append("settings.tier")

    request = service.instances().patch(  # patch sends request to update
        project=project_id,
        instance=instance_name,
        body=update_body
    )
    response = request.execute()  # execute runs that request

    print(f"Instance {instance_name} update request submitted. Response: {response}")
    return response

def process_csv_and_update_instances(file_path, project_id):
    df = pd.read_csv(file_path)
    
    # Iterate through rows and update instances as needed
    for index, row in df.iterrows():
        instance_name = row['Instance Name']
        current_cpu = row['CPU']
        current_memory = row['Memory']
        target_cpu = row['Target CPU']
        target_memory = row['Target Memory']
        
        if current_cpu != target_cpu or current_memory != target_memory:
            print(f"Updating instance {instance_name} from CPU: {current_cpu} to {target_cpu}, "
                  f"Memory: {current_memory} to {target_memory}")
            modify_cloudsql_instance(project_id, instance_name, target_cpu, target_memory)
        else:
            print(f"No update needed for instance {instance_name}")

if __name__ == "__main__":
    PROJECT_ID = "fks-ssi-cloud-sql"
    FILE_PATH = "tester.csv"  
    
    process_csv_and_update_instances(FILE_PATH, PROJECT_ID)
