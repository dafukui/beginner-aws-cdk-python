from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    core
)


class Qiita1204Stack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # IAMロールを作成
        my_role_ec2 = iam.CfnRole(
            self,
            id="my-role-ec2",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [{
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"}
                }]
            },
            description="the ec2 role",
            managed_policy_arns=[
                # "arn:aws:iam::aws:policy/AmazonS3FullAccess" # 付与したいアクセス権をリストする
            ],
            role_name="my-role-ec2",
            tags=[{
                    "key": "Name",
                    "value": "my-role-ec2"
            }]
        )
        # Instance Profileを作成
        my_instance_profile = iam.CfnInstanceProfile(
            self,
            id="my-instance-profile",
            roles=[my_role_ec2.ref]
        )

        # VPCを作成
        my_vpc = ec2.CfnVPC(
            self,
            id="my-vpc",
            cidr_block="192.168.0.0/16",
            enable_dns_hostnames=True,
            tags=[{
                    "key": "Name",
                    "value": "my-vpc"
            }]
        )

        # Subnetを作成
        my_subnet_1 = ec2.CfnSubnet(
            self,
            id="my-subnet",
            cidr_block="192.168.0.0/24",
            vpc_id=my_vpc.ref,
            availability_zone=core.Fn.select(0, core.Fn.get_azs("")),
            tags=[{
                    "key": "Name",
                    "value": "my-subnet-1"
            }]
        )

        # Internet Gatewayを作成
        my_igw = ec2.CfnInternetGateway(
            self,
            id="my-igw",
            tags=[{
                    "key": "Name",
                    "value": "my-igw"
            }]
        )
        # Internet Gatewayをアタッチ
        ec2.CfnVPCGatewayAttachment(
            self,
            id="my-igw-attachment",
            vpc_id=my_vpc.ref,
            internet_gateway_id=my_igw.ref
        )

        # Routetableを作成
        my_rtb = ec2.CfnRouteTable(
            self,
            id="my-rtb",
            vpc_id=my_vpc.ref,
            tags=[{
                    "key": "Name",
                    "value": "my-rtb"
            }]
        )
        # Routetableとサブネットの関連付け
        ec2.CfnSubnetRouteTableAssociation(
            self,
            id="my-rtb-association",
            route_table_id=my_rtb.ref,
            subnet_id=my_subnet_1.ref
        )

        # Routeの設定
        my_rt = ec2.CfnRoute(
            self,
            id="my-rt",
            route_table_id=my_rtb.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=my_igw.ref
        )

        # Security Groupの作成
        my_sg_ec2 = ec2.CfnSecurityGroup(
            self,
            id="my-sg-ec2",
            vpc_id=my_vpc.ref,
            group_description="my-sg-ec2",
            group_name="my-sg-ec2",
            security_group_ingress=[
                ec2.CfnSecurityGroup.IngressProperty(
                    ip_protocol="tcp",
                    cidr_ip="0.0.0.0/0",
                    from_port=22,
                    to_port=22
                )
            ],
            tags=[{
                    "key": "Name",
                    "value": "my-sg-ec2"
            }]
        )

        #  AMIを指定してimage_idを取得
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
            cpu_type=ec2.AmazonLinuxCpuType.X86_64
        ).get_image(self).image_id

        # EC2を作成
        my_ec2 = ec2.CfnInstance(
            self,
            id="my-ec2",
            availability_zone=core.Fn.select(0, core.Fn.get_azs("")),
            block_device_mappings=[
                ec2.CfnInstance.BlockDeviceMappingProperty(
                    device_name="/dev/sda1",
                    ebs=ec2.CfnInstance.EbsProperty(
                        delete_on_termination=True,
                        encrypted=False,
                        volume_size=10,
                        volume_type="gp2"
                    )
                )
            ],
            credit_specification=ec2.CfnInstance.CreditSpecificationProperty(
                cpu_credits="standard"
            ),
            iam_instance_profile=my_instance_profile.ref,
            image_id=amzn_linux,
            instance_type="t2.micro",
            security_group_ids=[my_sg_ec2.ref],
            subnet_id=my_subnet_1.ref,
            tags=[{
                    "key": "Name",
                    "value": "my-ec2"
            }]
        )