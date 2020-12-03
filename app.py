#!/usr/bin/env python3

from aws_cdk import core

from qiita_1204.qiita_1204_stack import Qiita1204Stack


app = core.App()
Qiita1204Stack(app, "qiita-1204", env={'region': 'us-east-1'}) # お好みのリージョンを指定

app.synth()
