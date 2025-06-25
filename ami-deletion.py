import boto3

def get_all_amis():
    return boto3.client('ec2').describe_images(Owners=['self'])['Images']

def get_used_amis_in_ec2():
    ec2 = boto3.client('ec2')
    used = {}
    for r in ec2.describe_instances()['Reservations']:
        for i in r['Instances']:
            img = i['ImageId']
            used.setdefault(img, []).append(f"EC2 Instance {i['InstanceId']}")
    return used

def get_used_amis_in_asg_templates():
    ec2 = boto3.client('ec2')
    used = {}
    for tpl in ec2.describe_launch_templates()['LaunchTemplates']:
        ver = ec2.describe_launch_template_versions(
            LaunchTemplateId=tpl['LaunchTemplateId'], Versions=['$Latest'])
        for v in ver['LaunchTemplateVersions']:
            img = v.get('LaunchTemplateData', {}).get('ImageId')
            if img:
                used.setdefault(img, []).append(f"Launch Template {tpl['LaunchTemplateName']}")
    return used

def get_used_amis_in_asg_configs():
    asg = boto3.client('autoscaling')
    used = {}
    for cfg in asg.describe_launch_configurations()['LaunchConfigurations']:
        if 'ImageId' in cfg:
            used.setdefault(cfg['ImageId'], []).append(f"Launch Config {cfg['LaunchConfigurationName']}")
    return used

def collect_all_used_amis():
    used = {}
    for d in [get_used_amis_in_ec2(), get_used_amis_in_asg_templates(), get_used_amis_in_asg_configs()]:
        for k, v in d.items():
            used.setdefault(k, []).extend(v)
    return used

def delete_unused_amis():
    ec2 = boto3.client('ec2')
    all_amis = get_all_amis()
    used_amis = collect_all_used_amis()

    for image in all_amis:
        ami_id = image['ImageId']
        name = image.get('Name', 'Unnamed')

        if ami_id not in used_amis:
            print(f"Deleting AMI {ami_id} ({name}) …")
            # ec2.deregister_image(ImageId=ami_id)
            for bd in image.get('BlockDeviceMappings', []):
                snap = bd.get('Ebs', {}).get('SnapshotId')
                if snap:
                    try:
                        # ec2.delete_snapshot(SnapshotId=snap)
                        print(f" → Deleted snapshot {snap}")
                    except Exception as e:
                        print(f" ⚠️ Snapshot deletion failed for {snap}: {e}")
        else:
            print(f"Skipping in-use AMI: {ami_id} ({name})")
            for usage in used_amis[ami_id]:
                print(f"   Used by: {usage}")

if __name__ == "__main__":
    delete_unused_amis()