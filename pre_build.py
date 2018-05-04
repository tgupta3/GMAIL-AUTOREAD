import sys
import boto3
import yaml
import re

def main():
    with open("serverless.yml",'r') as svl_yaml:
        try:
            svl_param = yaml.load(svl_yaml)
            ssm_kms_key = re.search(r'\${ssm:(.*?)(\~.*|})',svl_param['provider']['environment']['KMS_KEY']).group(1)
            
            ssm_kms_arn = re.search(r'\${ssm:(.*?)(\~.*|})',svl_param['functions']['starter']['iamRoleStatements'][0]['Resource']).group(1)
            ssm_cw_event = re.search(r'\${ssm:(.*?)(\~.*|})',svl_param['functions']['starter']['events'][0]['schedule']['name']).group(1)
            
            client_ssm = boto3.client('ssm')
            print ssm_kms_arn, ssm_cw_event, ssm_kms_key
            
            
            return (True)
        except  Exception as e :
            print (e)
            return (False)
            
if __name__ == '__main__':
        sys.exit(main())
        