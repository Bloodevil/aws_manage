import boto3
import subprocess

def get_all_instances(ec2, region):
    ec2 = ec2.describe_instances()
    reservations = ec2['Reservations']
    instances = []
    for reserv in reservations:
        for instance in reserv['Instances']:
            name = instance.get('Tags', 'noname')
            if name != 'noname':
                name = name[0]['Value']
            net = instance.get('NetworkInterfaces',[])
            if net:
                net = net[0]
                private_ip = net.get('PrivateIpAddress', '')
                public_ip = net.get('Association', {}).get('PublicIp', 'no public ip')
                pemfile = instance['KeyName']
                instances.append({'name': '_'.join([region, name]),
                    'private_ip': private_ip,
                    'public_ip': public_ip,
                    'pemfile' : pemfile,
                    'status' : instance['State']['Name']})
    return instances

def ssh_config(instance):
    string = """
Host %s
    Hostname %s
    #private_ip %s
    Port 22
    User centos
    IdentityFile ~/.ssh/%s
    """
    return string%(instance['name'], instance['public_ip'],
            instance['private_ip'], instance['pemfile'])

def make_ssh_config():
    regions = boto3.client('ec2').describe_regions()['Regions']
    for region in regions:
        print("#%s"%region['RegionName'])
        ec2 = boto3.client('ec2', region_name=region['RegionName'])
        instances = get_all_instances(ec2, region['RegionName'])
        for instance in instances:
            if instance['status'] == 'running':
                print(ssh_config(instance))

def get_public_by_private(private_ip):
    public_ip = ""
    return public_ip

def loadbalancer_instances(name='loadbalancer_name', region='us-east-1'):
    client = boto3.client('elb', region_name=region)
    ec2 = boto3.resource('ec2', region_name=region)
    descriptions = client.describe_load_balancers(LoadBalancerNames=[name])['LoadBalancerDescriptions']
    instances = descriptions[0]['Instances']
    result = []
    for instance in instances:
        ins = ec2.Instance(instance['InstanceId'])
        result.append({'private_ip': ins.private_ip_address,
            'public_ip': ins.public_ip_address,
            'pemfile': ins.key_name + '.pem',
            'tags': ins.tags,
            'InstanceId': instance['InstanceId']
            })

    return result

# instance = { 'pemfile' : filepath, 'public_ip': public_ip}
def remote_ssh_command(instance, command, user='centos'):
    command = 'ssh -i ~/.ssh/%s -t %s@%s \'%s\''%(instance['pemfile'],
            user,
            instance['public_ip'],
            command)
    ps = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read().decode('utf-8')
    ps.stdout.close()
    ps.wait()
    return output


def deregister_instances_from_load_balancer(name='loadbalancer_name',
        instances=[], region='us-east-1'):
    client = boto3.client('elb', region_name=region)
    return client.deregister_instances_from_load_balancer(LoadBalancerName=name,
            Instances=instances)

if __name__ == "__main__":
    make_ssh_config()
