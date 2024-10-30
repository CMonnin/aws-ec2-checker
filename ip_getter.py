import boto3
from botocore.exceptions import ClientError


def ip_getter(tag_name, region):
    """
    Get the public IP address of an EC2 instance tagged with Name: factorio
    Returns:
        str: Public IP address if found, None otherwise
    """
    try:
        ec2 = boto3.client("ec2", region)

        response = ec2.describe_instances(
            Filters=[
                {"Name": "tag:Name", "Values": [tag_name]},
            ]
        )

        if not response["Reservations"]:
            print("No instances found with tag Name: factorio")
            return None

        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                for interface in instance["NetworkInterfaces"]:
                    association = interface.get("Association")
                    if association:
                        public_ip = association.get("PublicIp")
                        if public_ip:
                            return public_ip

        print("No public IP found for factorio instance")
        return None

    except ClientError as e:
        print(f"Error retrieving instance information: {e}")
        return None
