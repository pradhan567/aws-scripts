import boto3

def get_all_amis():
    ec2 = boto3.client('ec2')
    images = ec2.describe_images(Owners=['self'])['Images']
    return images

def get_all_used_amis():
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances()
    used_amis = set()
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            used_amis.add(instance['ImageId'])
    return used_amis

def delete_unused_amis():
    ec2 = boto3.client('ec2')
    all_amis = get_all_amis()
    used_amis = get_all_used_amis()

    for image in all_amis:
        ami_id = image['ImageId']
        name = image.get('Name', 'Unnamed')

        if ami_id not in used_amis:
            print(f"Deleting AMI: {ami_id} ({name})")
            # ec2.deregister_image(ImageId=ami_id)

            # # Optionally delete associated snapshots
            # for mapping in image.get('BlockDeviceMappings', []):
            #     if 'Ebs' in mapping and 'SnapshotId' in mapping['Ebs']:
            #         snapshot_id = mapping['Ebs']['SnapshotId']
            #         try:
            #             ec2.delete_snapshot(SnapshotId=snapshot_id)
            #             print(f"Deleted snapshot: {snapshot_id}")
            #         except Exception as e:
            #             print(f"Failed to delete snapshot {snapshot_id}: {e}")
        else:
            print(f"AMI in use, skipping: {ami_id} ({name})")

if __name__ == "__main__":
    delete_unused_amis()
