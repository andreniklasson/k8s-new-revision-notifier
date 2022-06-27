# Kubernetes Deployment Revision Notifier
A lightweight service that sends notifications to a slack channel when new revisions of deployments are discovered. It will send an additional notification if the revision has been successfully rolled out or if the rollout exceeds a given time limit.

No public image is provided. If you want to use it you have to build and push it to your own registry. Update the _SLACK URL_ and _IMAGE URL_ in the StatefulSet accordingly.

## Caution
I would not recommend the use of this service when the notification is business critical. It holds the state of all deployments in memory; if a new revision is applied during a period where the notifier is in a non running state, it will be missed.