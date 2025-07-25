import os
import json
import uuid
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from flask import Flask, request, jsonify

# Define Flask routes
app = Flask(__name__)
@app.route("/apis/acme.easydns.com/v1alpha1/challenges", methods=["POST"])
def handle_acme_challenge():
    solver = AcmeSolver()
    return solver.run()

@app.route("/apis/acme.easydns.com/v1alpha1", methods=["GET"])
def discovery():
    return jsonify({
        "kind": "APIResourceList",
        "apiVersion": "v1",
        "groupVersion": "acme.easydns.com/v1alpha1",
        "resources": [
            {
                "name": "challenges",
                "kind": "Challenge",
                "version": "v1alpha1"
            }
        ]
    }), 200

class AcmeSolver:
    def __init__(self):
        self.payload = json.loads(request.data)
        log("FULL PAYLOAD FROM CERT-MANAGER: " + json.dumps(self.payload, indent=2))

        self.request = self.payload["request"]
        self.request_uid = self.request.get("uid")

        # cert-manager will send either: "Present" or "CleanUp"
        self.operation = self.request.get("action")

        self.cert_cn = self.request["dnsName"]
        self.zone = self.request.get("resolvedZone")[:-1]

        self.required_txt_record = self.request["key"]
        self.resolved_fqdn = self.request["resolvedFQDN"]

        self.easydns_api_token = os.environ['EASYDNS_API_TOKEN']
        self.easydns_api_token_name = os.environ['EASYDNS_API_TOKEN_NAME']
        self.auth = HTTPBasicAuth(self.easydns_api_token_name, self.easydns_api_token)

        self.base_url = "https://rest.easydns.net"
        self.acme_challenge_record = self.assemble_acme_record()

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        self.api_payload = {
            "domain": self.zone,
            "host": self.acme_challenge_record,
            "ttl": 300,
            "type": "TXT",
            "rdata": self.required_txt_record
        }


    def run(self):
        if self.operation == "CleanUp":
            self.delete_record()
        else:
            self.present()

        resp = {"uid": self.request_uid, "success": True}

        return jsonify({"response": resp})

        log("Response to cert-manager: " + json.dumps(resp, indent=2))


    def present(self):
        if self.check_record_exists():
            self.update_record()
        else:
            self.create_record()


    def assemble_acme_record(self):
        if not self.cert_cn.endswith(f".{self.zone}"):
            raise ValueError("Challenge FQDN doesn't match known zone")
        acme_challenge_record = self.cert_cn[: -len(self.zone) - 1]
        return f"_acme-challenge.{acme_challenge_record}"


    def check_record_exists(self):
        search_url = f"{self.base_url}/zones/records/all/{self.zone}/search/{self.acme_challenge_record}"
        resp = requests.get(search_url, headers=self.headers, auth=self.auth).json()

        log("EASYDNS SEARCH RESPONSE: " + json.dumps(resp, indent=2))

        if resp.get('count', 0) != 0:
            self.record_id = resp['data'][0]['id']
            return True
        return False


    def create_record(self):
        url = f"{self.base_url}/zones/records/add/{self.zone}/TXT"
        requests.put(url, headers=self.headers, auth=self.auth, json=self.api_payload)


    def update_record(self):
        url = f"{self.base_url}/zones/records/{self.record_id}"
        requests.post(url, headers=self.headers, auth=self.auth, json=self.api_payload)


    def delete_record(self):
        if self.check_record_exists():
            url = f"{self.base_url}/zones/records/{self.zone}/{self.record_id}"
            requests.delete(url, headers=self.headers, auth=self.auth)


def log(msg, level="INFO"):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    print(f"[{level}] {timestamp} {msg}")


# This app is being called by gunicorn in prod -  to enable proper TLS support.
# This can be used when testing the app locally.
#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=8443)
