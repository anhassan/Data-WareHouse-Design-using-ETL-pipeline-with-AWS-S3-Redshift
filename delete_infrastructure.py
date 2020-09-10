import boto3
import json
import configparser

def delete_cluster(config,KEY,SECRET):
    
    DWH_CLUSTER_IDENTIFIER = config.get("DWH","DWH_CLUSTER_IDENTIFIER")
    redshift = boto3.client('redshift',aws_access_key_id=KEY,aws_secret_access_key=SECRET,region_name='us-west-2')
    redshift.delete_cluster( ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,  SkipFinalClusterSnapshot=True)
    waiter = redshift.get_waiter('cluster_deleted')
    waiter.wait(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)


def delete_iam_role(config,KEY,SECRET):
    
    DWH_IAM_ROLE_NAME = config.get("DWH","DWH_IAM_ROLE_NAME")
    iam = boto3.client('iam',aws_access_key_id=KEY,aws_secret_access_key=SECRET,region_name='us-west-2')
    iam.detach_role_policy(RoleName=DWH_IAM_ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
    iam.delete_role(RoleName=DWH_IAM_ROLE_NAME)
    
    


def main():
    
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    
    KEY = config.get("AWS","KEY")
    SECRET = config.get("AWS","SECRET")
   
    print("Deleting Iam role.....")
    delete_iam_role(config,KEY,SECRET)
    
    print("Deleting RedShift Cluster...... ")
    delete_cluster(config,KEY,SECRET)
    
    
    print("Deleted all the infrastructure....")


if __name__ == "__main__":
    main()