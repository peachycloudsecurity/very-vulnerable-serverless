from flask import Flask, redirect, url_for, request, render_template, jsonify
import urllib.request
import subprocess
import json
import datetime as date
import re
import pickle
import base64

app = Flask(__name__)
app.secret_key = 'ThisisSuperFlagBySecurityDojo'


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# SLS-1: Injection Vulnerability
# User input directly interpolated into response without sanitization
@app.route('/welcome/<name>')
def success(name):
    return "<html><body><h2>welcome %s</h2></body></html>" % name


# SLS-1: Injection Vulnerability
# User-controlled input passed through without validation
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['name']
        return redirect(url_for('success', name=user))
    else:
        user = request.args.get('name')
        return redirect(url_for('success', name=user))


# SLS-3: SSRF / Lambda Runtime Invocation
# Fetches arbitrary URLs including internal Lambda runtime API
# Try: /redirect?url=http://169.254.100.1:9001/2018-06-01/runtime/invocation/next
@app.route('/redirect')
def web():
    try:
        site = request.args.get('url')
        response = urllib.request.urlopen(site)
        output = json.dumps(response.read().decode('utf-8'))
        return jsonify({"output": output}), 200
    except Exception as e:
        return f"Error Occurred: {e}"


# SLS-1: Command Injection + SLS-6: Insecure IAM Permissions
# Arbitrary OS command execution via shell=True
# Combined with overly permissive s3:* IAM role allows credential theft
# Try: /date?exec=printenv (leaks AWS credentials)
@app.route('/date')
def command():
    try:
        cmd = request.args.get('exec')
        count = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        stdout, stderr = count.communicate()
        return jsonify({"output": stdout.decode()}), 200
    except Exception as e:
        return f"Error Occurred: {e}"


# SLS-10: ReDoS (Regular Expression Denial of Service)
# Catastrophic backtracking with evil regex ^(a+)+b$
# Try: /redos?string=aaaaaaaaaaaaaaaaaaaaaaaaaaa (increasing 'a' count causes exponential time)
@app.route('/redos')
def redos():
    try:
        user_string = request.args.get('string')
        start_time = date.datetime.now()

        malicious_regex = "^(a+)+b$"
        match = re.match(malicious_regex, user_string)

        end_time = date.datetime.now()

        if match:
            return "<html><body><p><h3 style='background-color:SpringGreen;'>String matches regex</p><p>Response time: {}</h3></p></body></html>".format(end_time - start_time)
        else:
            return "<html><body><p><h3 style='background-color:IndianRed;'>String does not match regex</p><p>Response time: {}</h3></p></body></html>".format(end_time - start_time)
    except Exception as e:
        return f"Error Occurred: {e}"


# SLS-2: Insecure Deserialization
# Unpickles arbitrary user-supplied data — leads to RCE
# Reference: https://github.com/CalfCrusher/Python-Pickle-RCE-Exploit
@app.route('/deserial', methods=['POST'])
def deserial():
    try:
        data = base64.urlsafe_b64decode(request.form['pickled'])
        pickle.loads(data)
        return 'pickled successfully', 200
    except Exception as e:
        return f'Error occurred while pickling: {e}', 500
