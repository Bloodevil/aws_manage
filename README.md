# aws_manage

How to add aws credential file
========
1. login aws console.
2. go to "My Security Credentials tab"
3. open the "Access Keys (Access Key ID and Secret Access Key)" tab and create new access key
4. make ~/.ssh/credentials file and add like below
*without ", '*
    [default]
    aws_access_key_id = ABCDASDFASDFADSFASDF
    aws_secret_access_key = adfadfkjalkejgadfasdfajsdkfljasdkfj
    region = us-east-1

Run aws_manage
======
    python3.5 aws_manage.py

