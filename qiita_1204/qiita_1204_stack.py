from aws_cdk import (
    aws_ec2 as ec2,
    core
)


class Qiita1204Stack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPCを作成
        my_vpc = ec2.Vpc(
            self,
            id="my-vpc",
            cidr="192.168.0.0/16",
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="my-public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ]
        )

        # セキュリティグループを作成
        my_ec2_security_group = ec2.SecurityGroup(
            self,
            id="my-ec2-sg",
            vpc=my_vpc,
            allow_all_outbound=True,
            security_group_name="my-ec2-sg"
        )

        # 作成したセキュリティグループにインバウンド許可設定を追加
        my_ec2_security_group.add_ingress_rule(
            # peer=ec2.Peer.ipv4("{IPアドレスを指定}"),
            peer=ec2.Peer.ipv4("0.0.0.0/0"),
            connection=ec2.Port.tcp(22),
            description="allow ssh access"
        )

        #  AMIを指定
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
            cpu_type=ec2.AmazonLinuxCpuType.X86_64
        )

        # EC2インスタンスを作成
        my_ec2_instance = ec2.Instance(
            self,
            id="my-ec2-instance",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2,
                ec2.InstanceSize.MICRO
            ),
            machine_image=amzn_linux,
            vpc=my_vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            instance_name="my-ec2-instance",
            security_group=my_ec2_security_group
        )
