# cert_validity

A small Python utility that retrieves and analyzes TLS/SSL certificate validity from remote services.

The script connects to a host, fetches the presented X.509 certificate, and extracts useful metadata such as:

- Certificate issuer
- Validity period (`notBefore` / `notAfter`)
- Remaining validity time
- Expiration status

This makes it useful for monitoring certificate expiration and detecting services that may soon experience TLS outages.

## Usage

```bash
# HTTPS
python cert_validity.py example.com 443

# IMAPS
python cert_validity.py mail.example.com 993

# POP3S
python cert_validity.py mail.example.com 995

# SMTPS
python cert_validity.py mail.example.com 465
