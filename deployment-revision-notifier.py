from kubernetes import client, config
from threading import Thread
from slack_sdk.webhook import WebhookClient
import os
import time

SLACK_URL = os.environ['SLACK_URL']
REVISION_TIMEOUT = int(os.environ['REVISION_TIMEOUT'])

config.load_incluster_config()
v1 = client.AppsV1Api()
webhook = WebhookClient(SLACK_URL)
service_dict = {}

def slack_notification(deployment_name, color, payload):
    response = webhook.send(
        attachments=[
            {
                "color": color,
                "fields": [
                { "title": deployment_name, "value": payload, "short": False }
                ]
            }
        ]
    )

def check_for_successful_rollout(deployment_name, timeout=REVISION_TIMEOUT):
    success = False
    start = time.time()
    while time.time() - start < timeout:
        response = v1.read_namespaced_deployment_status(deployment_name, "apps")
        status = response.status
        if (status.updated_replicas == response.spec.replicas and
                status.replicas == response.spec.replicas and
                status.available_replicas == response.spec.replicas and
                status.observed_generation >= response.metadata.generation):
            success = True
            break
        time.sleep(2)

    if success:
        slack_notification(deployment_name, "good", "Revision has successfully been deployed")
    else:
        slack_notification(deployment_name, "danger", "The rollout of the new revision has taken more than " + str(REVISION_TIMEOUT) + " seconds to complete")

def check_for_new_revision(deployment_name, revision):
    if (deployment_name not in service_dict or service_dict[deployment_name] != revision):
        service_dict[deployment_name] = revision
        slack_notification(deployment_name, "warning", "A new revision has been detected")

        thread = Thread(target=check_for_successful_rollout, args=(deployment_name,))
        thread.start()

if __name__ == "__main__":
    response = v1.list_deployment_for_all_namespaces(watch=False)
    for item in response.items:
        service_dict[item.metadata.name] = item.metadata.annotations['deployment.kubernetes.io/revision']

    while(1):
        response = v1.list_deployment_for_all_namespaces(watch=False)
        for deployment in response.items:
            check_for_new_revision(deployment.metadata.name, deployment.metadata.annotations['deployment.kubernetes.io/revision'])
        time.sleep(3)

