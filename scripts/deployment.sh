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
eb init -k erepie -p python-2.7 --region eu-west-3 facile-erp && echo "Beanstalk environment initialized" ||
echo "Beanstalk environment init failed"

# TODO last 2 days:
Create account for casoe
Create super user in AWS's casoe account
Create a database instance
Make the ElasticBeansTalk routine for deployment
Create File that gather every core information of application (aws web, etc)




