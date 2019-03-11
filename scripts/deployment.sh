#!/bin/bash

# Fork facile erp
git clone https://github.com/pierreGouedard/facile.git && cd facile && "facile ERP forked" ||
echo "fork of facile ERP failed"

# Install pip
sudo apt -q update && echo Y | sudo apt -q install python-pip && echo "python-pip installed" || echo "python-pip install failed"

# Install virtualenv and create it
sudo pip install virtualenv && virtualenv fvirt && source fvirt/bin/activate &&
echo "virtualenv created and activated" || echo "virtualenv created and activated"

# Install requirements
pip install -qr requirements.txt

# Install and init Elastic Beanstalk Environment
pip install -q awsebcli && echo "fvirt" > .ebignore &&
eb init -k erepie -p python-2.7 --region eu-west-3 casoe-erp && echo "Beanstalk environment initialized" ||
echo "Beanstalk environment init failed"

# It does not work now. Still, using eb configuration and changing line
# static: facileapp/static/ (change using eb config)
# application_path: run.py (change using eb config)
# instance_type: t2.medium  option (eb create --instance_type t2.medium)

# finally:
# Connect to instance (ssh with username 'ubunutu' or 'ec2-user')
# create secret-config file in /opt/python/current/app/secret-config-casoe.yaml

# Create application



