import configparser
import boto3
import json



def create_iam_role(config,KEY,SECRET):
    
            #Creating an iam client
            iam = boto3.client('iam',aws_access_key_id=KEY,aws_secret_access_key=SECRET,region_name='us-west-2')
            
            # Getting parameters from configuration file
            DWH_IAM_ROLE_NAME      = config.get("DWH", "DWH_IAM_ROLE_NAME")
            
            #Generating a Role policy document
            trust_relationship_policy_redshift = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "redshift.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
            #Creating an iam role
            try:
                
                dwhRole = iam.create_role(
                            RoleName=DWH_IAM_ROLE_NAME,
                            AssumeRolePolicyDocument=json.dumps(trust_relationship_policy_redshift))

            except Exception as e:
                print(e)
            
            try:
            # Attaching policies to the iam role
                policy_attach_res = iam.attach_role_policy(RoleName=DWH_IAM_ROLE_NAME,
                                        PolicyArn='arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess')
            except Exception as e:
                print(e)

            
            #Getting the resource name of the role
            roleArn = iam.get_role(RoleName=DWH_IAM_ROLE_NAME)['Role']['Arn']
            
            config['IAM_ROLE']['ROLE_ARN'] =  roleArn  

            with open('dwh.cfg', 'w') as configfile:    
                        config.write(configfile)
            
            
    


    
def create_redshift_cluster(config,KEY,SECRET):
    
    #Creating a redshift client
    redshift = boto3.client('redshift',aws_access_key_id=KEY,aws_secret_access_key=SECRET,region_name='us-west-2')
    
    #Creating an ec2 client
    ec2 = boto3.resource('ec2',aws_access_key_id=KEY,aws_secret_access_key=SECRET,region_name='us-west-2')
    
    
    # Getting cluster parameters from the configuration file
    
    DWH_CLUSTER_TYPE       = config.get("DWH","DWH_CLUSTER_TYPE")
    DWH_NUM_NODES          = config.get("DWH","DWH_NUM_NODES")
    DWH_NODE_TYPE          = config.get("DWH","DWH_NODE_TYPE")

    DWH_CLUSTER_IDENTIFIER = config.get("DWH","DWH_CLUSTER_IDENTIFIER")
    DWH_DB                 = config.get("DWH","DWH_DB")
    DWH_DB_USER            = config.get("DWH","DWH_DB_USER")
    DWH_DB_PASSWORD        = config.get("DWH","DWH_DB_PASSWORD")
    DWH_PORT               = config.get("DWH","DWH_PORT")
    roleArn                =config.get("IAM_ROLE","ROLE_ARN")

    
    
    #Creating a redshift cluster
    try:
        response = redshift.create_cluster(        
        # Add parameters for hardware
        DBName = DWH_DB, ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
        ClusterType = DWH_CLUSTER_TYPE,NodeType=DWH_NODE_TYPE,
        NumberOfNodes= int(DWH_NUM_NODES),
        

        # Add parameters for identifiers & credentials
        MasterUsername = DWH_DB_USER,
        MasterUserPassword = DWH_DB_PASSWORD,
        Port=int(DWH_PORT),
        
        # Add parameter for role (to allow s3 access)
        IamRoles = [roleArn]
        

         
        )
    except Exception as e:
        print(e)
        
      
    #Waiting for the cluster to be active
    waiter = redshift.get_waiter('cluster_available')
    waiter.wait(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER) 
    
    # To get cluster properties
    myClusterProps = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
    
    print("DWH_ENDPOINT = ",myClusterProps['Endpoint']['Address'])
    print("DWH_ROLE_ARN", myClusterProps['IamRoles'][0]['IamRoleArn'])
    
    config['CLUSTER']['DWH_ENDPOINT'] = myClusterProps['Endpoint']['Address']
    config['CLUSTER']['DWH_ROLE_ARN'] = myClusterProps['IamRoles'][0]['IamRoleArn']

    with open('dwh.cfg', 'w') as configfile:    
        config.write(configfile)
        
    print("through config", config.get("CLUSTER","DWH_ENDPOINT"))
    
    # Opening TCP port for connecting to the end point of the cluster
    try:
        vpc = ec2.Vpc(id=myClusterProps['VpcId'])
        defaultSg = list(vpc.security_groups.all())[0]
        print(defaultSg)
        print(defaultSg.group_name)

        defaultSg.authorize_ingress(
            GroupName= 'default' ,  
            CidrIp='0.0.0.0/0', 
            IpProtocol='TCP', 
            FromPort=int(DWH_PORT),
            ToPort=int(DWH_PORT)
            )
    except Exception as e:
        print("Port Already Configured...")
    
    
     
    
    
    
def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    
    KEY = config.get("AWS","KEY")
    SECRET = config.get("AWS","SECRET")
    
    create_iam_role(config,KEY,SECRET)
    create_redshift_cluster(config,KEY,SECRET)
    
    
if __name__ == "__main__":
    main()