import multiprocessing
import time
from google.cloud import dialogflowcx_v3 as dialogflow
from google.cloud import storage
import random
import uuid
import os

def get_project_id():
    storage_client = storage.Client()
    return storage_client.project

def create_session(project_id, location, agent_id, environment_id):
    session_id = str(uuid.uuid4())
    session_path = f"projects/{project_id}/locations/{location}/agents/{agent_id}/environments/{environment_id}/sessions/{session_id}"
    return session_path


def send_text_input(session_path, text, client_options):
    session_client = dialogflow.SessionsClient(client_options=client_options)
    request = dialogflow.DetectIntentRequest(
        session=session_path,
        query_input=dialogflow.QueryInput(
            text=dialogflow.TextInput(text=text),
            language_code="en"
        ),
    )
    response = session_client.detect_intent(request=request)
    return response.query_result


def simulate_conversation(project_id, location, agent_id, environment_prod, environment_default, client_options, no_match=False):
    environment_id = environment_prod if random.random() < 0.9 else environment_default
    session_path = create_session(
        project_id, location, agent_id, environment_id)
    print(f"Starting new conversation in {environment_id}...")

    conversation_flows = [
        ["Hi", "Tomorrow", "Advanced", "Ingrid"],
        ["Hi", "I don't want a lesson"]
    ]

    if no_match:
        num_utterances = random.randint(2, 5)
        conversation = ["Hi"] + \
            [f"random_text_{i}" for i in range(num_utterances)]
    else:
        conversation = random.choice(conversation_flows)

    for user_input in conversation:
        response = send_text_input(session_path, user_input, client_options)
        time.sleep(0.2)


def list_agents(project, location, client_options):
    client = dialogflow.AgentsClient(client_options=client_options)

    request = dialogflow.ListAgentsRequest(
        parent=f"projects/{project}/locations/{location}",
    )
    response = client.list_agents(request=request)
    return response, client

def list_environments(agent, client_options):
    client = dialogflow.EnvironmentsClient(
        client_options=client_options
    )

    request = dialogflow.ListEnvironmentsRequest(
        parent=agent,
    )
    response = client.list_environments(request=request)
    return response, client

def main():
    project_id = get_project_id()
    location = os.getenv("LOCATION", "global")
    if location == "global":
        client_options = {"api_endpoint": "dialogflow.googleapis.com"}
    else:
        client_options = {"api_endpoint": f"{location}-dialogflow.googleapis.com"}
    agents, agent_client = list_agents(project_id, location, client_options)
    for agent in agents:
        if "Booking" in agent.display_name:
            agent_id = agent_client.parse_agent_path(agent.name)['agent']
            environments, env_client = list_environments(
                agent.name, client_options)
            for environment in environments:
                if "prod" in environment.display_name:
                    environment_prod = env_client.parse_environment_path(environment.name)[
                        'environment']

    environment_default = "-"

    num_conversations = int(os.getenv("NUM_CONVERSATIONS", 1000)) // 5

    for i in range(num_conversations):
        no_match = random.random() < 0.3
        simulate_conversation(project_id, location, agent_id,
                              environment_prod, environment_default, client_options, no_match=no_match)
        time.sleep(0.2)


if __name__ == "__main__":
    num_processes = 5
    processes = [multiprocessing.Process(
        target=main) for _ in range(num_processes)]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
