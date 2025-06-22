"""
cert_validity.py
Checks for TLS cert validity in days
Author: guy.gold@open-xchange.com
"""

import socket
import ssl
import datetime
import argparse
import logging
import os
import sys


class CustomFormatter(logging.Formatter):
    def __init__(self, hostname, program_name):
        super().__init__()
        self.hostname = hostname
        self.program_name = program_name

    def format(self, record):
        parts = []
        parts.append(f"{record.getMessage()}")
        return " ".join(parts)


class CertChecker:
    def __init__(self, server, port, log_path=None):
        self.server = server
        self.port = port
        self.hostname = socket.gethostname()
        self.program_name = os.path.basename(__file__)
        self.logger = self._setup_logger(log_path)

    def _setup_logger(self, log_path):
        logger = logging.getLogger("cert_checker")
        logger.setLevel(logging.INFO)
        handler = (
            logging.FileHandler(log_path)
            if log_path and log_path != "-"
            else logging.StreamHandler(sys.stdout)
        )
        handler.setFormatter(CustomFormatter(
            self.hostname, self.program_name
        ))
        logger.addHandler(handler)
        return logger

    def check(self):
        try:
            # Top padding
            print()

            ip_address = socket.gethostbyname(self.server)
            self.logger.info(f"***Resolved {self.server} to {ip_address}***")

            context = ssl.create_default_context()
            with context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=self.server) as conn:
                conn.settimeout(10)
                conn.connect((self.server, self.port))
                cert = conn.getpeercert()
                not_after_str = cert.get("notAfter")
                if not not_after_str:
                    raise ValueError("Could not retrieve 'notAfter' from certificate.")
                not_after = datetime.datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                days_remaining = (not_after.date() - datetime.date.today()).days

                # Extract Subject CN
                subject = cert.get("subject", [])
                cn = None
                for attr in subject:
                    for key, value in attr:
                        if key == "commonName":
                            cn = value
                            break

                # Extract SANs
                san = []
                for ext in cert.get("subjectAltName", []):
                    if ext[0] == "DNS":
                        san.append(ext[1])

                self.logger.info(f"Certificate validity for {self.server}: {days_remaining} days")
                if cn:
                    self.logger.info(f"Subject: CN = {cn}")
                if san:
                    self.logger.info("X509v3 Subject Alternative Name: " + ", ".join(san))
            # Bottom padding
            print()

        except Exception as e:
            self.logger.error(f"Error retrieving certificate: {e}")
            sys.exit(1)
            # Ensure bottom padding even on error
            print()


def parse_args():
    parser = argparse.ArgumentParser(description="Check SSL certificate validity.")
    parser.add_argument("--server", required=True, help="Target server hostname")
    parser.add_argument("--port", type=int, default=443, help="Target port (default: 443)")
    return parser.parse_args()


def main():
    args = parse_args()
    checker = CertChecker(
        server=args.server,
        port=args.port,
    )
    checker.check()


if __name__ == "__main__":
    main()

