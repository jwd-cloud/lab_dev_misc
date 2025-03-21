from google.cloud import dialogflowcx_v3beta1
from google.cloud import storage
import os


def get_project_id():
    """Retrieve the Google Cloud project ID from the storage client."""
    storage_client = storage.Client()
    return storage_client.project


def list_agents(project, location, client_options):
    """List all agents in a given project and location."""
    client = dialogflowcx_v3beta1.AgentsClient(client_options=client_options)
    request = dialogflowcx_v3beta1.ListAgentsRequest(
        parent=f"projects/{project}/locations/{location}",
    )
    return client.list_agents(request=request)


def list_flows(agent, client_options):
    """List all flows for a given agent."""
    client = dialogflowcx_v3beta1.FlowsClient(client_options=client_options)
    request = dialogflowcx_v3beta1.ListFlowsRequest(parent=agent)
    return client.list_flows(request=request)


def list_flow_versions(flow, client_options):
    """List all versions for a given flow."""
    client = dialogflowcx_v3beta1.VersionsClient(client_options=client_options)
    request = dialogflowcx_v3beta1.ListVersionsRequest(parent=flow)
    return client.list_versions(request=request)


def list_playbooks(agent, client_options):
    """List all playbooks for a given agent."""
    client = dialogflowcx_v3beta1.PlaybooksClient(
        client_options=client_options)
    request = dialogflowcx_v3beta1.ListPlaybooksRequest(parent=agent)
    return client.list_playbooks(request=request)


def list_playbook_versions(playbook, client_options):
    """List all versions for a given playbook."""
    client = dialogflowcx_v3beta1.PlaybooksClient(
        client_options=client_options)
    request = dialogflowcx_v3beta1.ListPlaybookVersionsRequest(parent=playbook)
    return client.list_playbook_versions(request=request)


def list_tools(agent, client_options):
    """List all tools for a given agent."""
    client = dialogflowcx_v3beta1.ToolsClient(
        client_options=client_options)
    request = dialogflowcx_v3beta1.ListToolsRequest(parent=agent)
    return client.list_tools(request=request)


def list_tool_versions(tool, client_options):
    """List all versions for a given tool."""
    client = dialogflowcx_v3beta1.ToolsClient(
        client_options=client_options)
    request = dialogflowcx_v3beta1.ListToolVersionsRequest(parent=tool)
    return client.list_tool_versions(request=request)


def list_environments(agent, client_options):
    """List all environments for a given agent."""
    client = dialogflowcx_v3beta1.EnvironmentsClient(
        client_options=client_options)
    request = dialogflowcx_v3beta1.ListEnvironmentsRequest(parent=agent)
    return client.list_environments(request=request)


def get_agents(project, location, client_options, agent_prefix="Zermatt"):
    """Retrieve all agents with 'zermatt' in their display name."""
    agents = list_agents(project, location, client_options)
    return [agent for agent in agents if agent_prefix.lower() in agent.display_name.lower()]


def flow_version_exists(agents, client_options, display_name):
    """Check if a specific flow version exists in any of the matching agents."""
    for agent in agents:
        flows = list_flows(agent.name, client_options)
        for flow in flows:
            versions = list_flow_versions(flow.name, client_options)
            if any(display_name in version.display_name for version in versions):
                return True
    return False


def playbook_version_exists(agents, client_options, display_name):
    """Check if a specific playbook version exists in any of the matching agents."""
    for agent in agents:
        playbooks = list_playbooks(agent.name, client_options)
        for playbook in playbooks:
            versions = list_playbook_versions(playbook.name, client_options)
            if any(display_name in version.description for version in versions):
                return True
    return False

## turns out this is unimplemented in the python sdk
## you have to use the REST API
def tool_version_exists(agents, client_options, display_name):
    return False

    """Check if a specific playbook version exists in any of the matching agents."""
    for agent in agents:
        tools = list_tools(agent.name, client_options)
        for tool in tools:
            versions = list_tool_versions(tool.name, client_options)
            if any(display_name in version.description for version in versions):
                return True
    return False


def environment_matches(agents, client_options, display_name):
    """Check if a specific environment exists in any of the matching agents."""
    for agent in agents:
        environments = list_environments(agent.name, client_options)
        for environment in environments:
            if environment.display_name.lower() in environment.display_name.lower():
                return True
    return False

def webhook_override_matches(agents, client_options, env_name, suffix):
    """Check if a specific webhook override is configured correctly for the envrionment"""
    for agent in agents:
        environments = list_environments(agent.name, client_options)
        for environment in environments:
            if environment.display_name.lower() in environment.display_name.lower():
                try:
                    overrides = environment.webhook_config.webhook_overrides
                except AttributeError:
                    return False 

                for override in overrides:
                    try:
                        uri = override.generic_web_service.uri
                        if suffix in uri:
                            return True
                    except AttributeError:
                        continue 
    return False


# Setup project and client options
PROJECT = get_project_id()
LOCATION = os.getenv("LOCATION", "global")
CLIENT_OPTIONS = {"api_endpoint": f"{LOCATION}-dialogflow.googleapis.com" if LOCATION !=
                  "global" else "dialogflow.googleapis.com"}
AGENT_PREFIX = "Zermatt"
ENVIRONMENT = "prod"

# Get filtered agents
agents = get_agents(PROJECT, LOCATION, CLIENT_OPTIONS)



# Perform checks
flow_version_created = flow_version_exists(
    agents, CLIENT_OPTIONS, "1.0.0")
playbook_version_created = playbook_version_exists(
    agents, CLIENT_OPTIONS, "1.0.0")
tool_version_created = tool_version_exists(
    agents, CLIENT_OPTIONS, "1.0.0")
env_matches = environment_matches(agents, CLIENT_OPTIONS, ENVIRONMENT)
override_match = webhook_override_matches(agents, CLIENT_OPTIONS, ENVIRONMENT, "v1.0.2")

# Output results
print(f"Flow version created: {flow_version_created}")
print(f"Playbook version created: {playbook_version_created}")
print(f"Environment matches: {env_matches}")
print(f"Tool version created: {tool_version_created}")
print(f"Webhook override matches: {override_match}")
