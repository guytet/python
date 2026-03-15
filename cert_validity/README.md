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
# HTTPS (Default check)
python cert_validity.py --server example.com

# IMAPS
python cert_validity.py --server imap.example.com --port 993

# POP3S
python cert_validity.py --server pop.example.com --port 995

# SMTPS
python cert_validity.py --server smtp.example.com --port 465
