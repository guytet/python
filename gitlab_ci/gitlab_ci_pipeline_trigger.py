import argparse
import requests

class GitLabPipelineTrigger:
    def __init__(self, token, ref, url, project_id, variables=None):
        self.token = token
        self.ref = ref
        self.url = url.rstrip("/")
        self.project_id = project_id
        self.variables = variables or {}

    def build_url(self):
        return f"{self.url}/api/v4/projects/{self.project_id}/trigger/pipeline"

    def trigger(self):
        payload = {
            'token': self.token,
            'ref': self.ref,
        }

        for key, value in self.variables.items():
            payload[f'variables[{key}]'] = value

        response = requests.post(self.build_url(), data=payload)

        if response.status_code == 201:
            print("Pipeline triggered successfully.")
            print(response.json())
        else:
            print("Failed to trigger pipeline.")
            print(f"Status Code: {response.status_code}")
            print(response.text)

def parse_variable(kv_string):
    if "=" not in kv_string:
        raise argparse.ArgumentTypeError("Variables must be in KEY=VALUE format")
    key, value = kv_string.split("=", 1)
    return key, value

def main():
    parser = argparse.ArgumentParser(description="Trigger a GitLab CI pipeline via API.")

    parser.add_argument("--url", required=True, help="(required) Base URL of the GitLab instance (e.g. https://gitlab.example.com)")
    parser.add_argument("--project-id", required=True, help="(required) Numeric project ID in GitLab")
    parser.add_argument("--ref", required=True, help="(required) Git branch or tag to trigger")
    parser.add_argument("--token", required=True, help="(required) GitLab pipeline trigger token")

    parser.add_argument(
        "--variable",
        action='append',
        type=parse_variable,
        metavar="KEY=VALUE",
        help="(optional) CI variable in KEY=VALUE format; can be used multiple times"
    )

    args = parser.parse_args()

    variables = dict(args.variable) if args.variable else {}

    trigger = GitLabPipelineTrigger(
        url=args.url,
        project_id=args.project_id,
        ref=args.ref,
        token=args.token,
        variables=variables
    )

    trigger.trigger()

if __name__ == "__main__":
    main()

