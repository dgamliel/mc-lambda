import urllib3
import json
import boto3

class CommandRunner:
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.ssm_client  = boto3.client('ssm')
        self.command_output = None

    def run_command(self, command):
        command = command.strip().split('\n')
        response = self.ssm_client.send_command(
            InstanceIds=[self.instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={
                'commands': command
            }
        )

        self.last_ran_cmd_id = self.get_command_output(response['Command']['CommandId'])

        return response

    def run_s3_script(self, s3_uri, *args):
        #Get the additional params from  the positional arguments
        additional_params = ' '.join(args)
        script_name = s3_uri.split('/')[-1]

        #Run the script
        command =  f"""
        #!/bin/sh
        cd /home/ec2-user/
        aws s3 cp {s3_uri} . 
        chmod +x {script_name}
        ./{script_name} {additional_params}
        """

        return self.run_command(command)


    def get_command_output(self, command_id):
        response = self.ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=self.instance_id
        )

        return response

class JarManager:
    def __init__(self):
        self.server_jar_url = None
        self.latest_version = self.get_latest_version()

        #Check that the latest version of minecraft is what we have in our s3 path
        #If not, download the latest version and upload it to s3
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('dgamliel-minecraft-jars')

        contains_latest_version = False

        #Check all the objects under the prefix server_jars/
        for obj in bucket.objects.filter(Prefix='server_jars/'):
            #If the object is the latest version, set the server_jar_url to the url of the object
            if obj.key == f'server_jars/v{self.latest_version}.jar':
                self.server_jar_url = obj.key
                contains_latest_version = True
                break

        if not contains_latest_version:
            #If the bucket doesn't contain the latest version, download the latest version and upload it to s3
            self.server_jar_url = self.get_jar_url(self.latest_version)
            jar_url = self.server_jar_url
            jar_bytes = self.download_jar(jar_url)

            to_upload =s3.Object('dgamliel-minecraft-jars', f'server_jars/v{self.latest_version}.jar')
            to_upload.put(Body=jar_bytes)


    def download_json(self, url):
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        return json.loads(response.data.decode('utf-8'))

    def get_latest_version(self):
        minecraft_version = self.download_json('https://launchermeta.mojang.com/mc/game/version_manifest.json')
        latest_version = minecraft_version['latest']['release']

        return latest_version

    def get_jar_url(self, version=None):
        version = version or self.get_latest_version()

        version_manifest = self.download_json('https://launchermeta.mojang.com/mc/game/version_manifest.json')
        versions         = version_manifest['versions']

        version_url = None

        for _ in versions:
            if _['id'] == version:
                version_url = _['url']
                break

        if version_url is None:
            raise Exception(f'Version {version} not found')

        version_json   = self.download_json(version_url)
        server_jar_url = version_json['downloads']['server']['url']

        return server_jar_url

    def download_jar(self, url):
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        return response.data

