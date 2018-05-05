import sys
import boto3
import yaml
import re

def ssm_verify_param(client,params):
    try:
        response = client.get_parameters(Names=params)
        if (response['InvalidParameters']):
            return 1
        return 0 
    except Exception as e:
        print (e)
        return 1
    
    
def main():
    with open("serverless.yml",'r') as svl_yaml:
        try:
            svl_param = yaml.load(svl_yaml)
            ssm_kms_key = re.search(r'\${ssm:(.*?)(\~.*|})',svl_param['provider']['environment']['KMS_KEY']).group(1)
            
            ssm_kms_arn = re.search(r'\${ssm:(.*?)(\~.*|})',svl_param['functions']['starter']['iamRoleStatements'][0]['Resource']).group(1)
            ssm_cw_event = re.search(r'\${ssm:(.*?)(\~.*|})',svl_param['functions']['starter']['events'][0]['schedule']['name']).group(1)
            client_ssm = boto3.client('ssm')
            #print ssm_kms_arn, ssm_cw_event, ssm_kms_key
            
            return ssm_verify_param(client_ssm,
                [
                ssm_kms_key,
                ssm_kms_arn,
                ssm_cw_event
                ])
                
        except  Exception as e :
            print (e)
            return 1
            
if __name__ == '__main__':
        sys.exit(main())
        