# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

from monasca_agent.collector.checks import utils

kubernetes_connector = utils.KubernetesConnector()
print kubernetes_connector.get_agent_pod_host(3, return_host_name=True)
