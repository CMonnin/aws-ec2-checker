import boto3
from botocore.exceptions import ClientError

def ip_getter(stack_name, region):
    """
    Get the public IP address of an EC2 instance in a specific ASG within a CloudFormation stack
    Args:
        stack_name (str): Name of the CloudFormation stack
        region (str): AWS region
    Returns:
        str: Public IP address if found, None otherwise
    """
    try:
        ec2 = boto3.client("ec2", region)
        response = ec2.describe_instances(
            Filters=[
                {"Name": "tag:aws:cloudformation:stack-name", "Values": [stack_name]},
                {"Name": "tag:aws:autoscaling:groupName", "Values": [f"{stack_name}-asg"]},
                {"Name": "instance-state-name", "Values": ["running"]}
            ]
        )
        
        if not response["Reservations"]:
            print(f"No running instances found in ASG: {stack_name}-asg")
            return None
        
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                for interface in instance["NetworkInterfaces"]:
                    association = interface.get("Association")
                    if association:
                        public_ip = association.get("PublicIp")
                        if public_ip:
                            print(public_ip)
                            return public_ip
        print(f"No public IP found for instances in ASG: {stack_name}-asg")
        return None
    except ClientError as e:
        print(f"Error retrieving instance information: {e}")
        return None
