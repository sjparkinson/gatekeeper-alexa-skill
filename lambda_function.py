import json
import logging
import requests
import uuid

PARTICLE_CLOUD_API_ENDPOINT = 'https://api.particle.io'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# Main function entrypoint, handles request routing.
def lambda_handler(event, context):
    logger.info("Recieved event: {}".format(json.dumps(event)))

    # The Smart Home API request namespace.
    namespace = event['header']['namespace']

    if namespace == 'Alexa.ConnectedHome.Discovery':
        return handle_device_discovery(namespace)

    if namespace == 'Alexa.ConnectedHome.Control':
        if event['header']['name'] == 'TurnOnRequest':
            return handle_turn_on_control(namespace, event['payload'])

        if event['header']['name'] == 'HealthCheckRequest':
            return handle_health_check(namespace, event['payload'])


def handle_device_discovery(namespace):
    logger.info('Handling discovery event.')

    headers = {
        'messageId': str(uuid.uuid4()),
        'name': 'DiscoverAppliancesResponse',
        'namespace': namespace,
        'payloadVersion': '2',
    }

    payload = {
        'discoveredAppliances': [
            {
                'applianceId': '20003a000747343232363230',
                'manufacturerName': 'Particle Industries, Inc.',
                'modelName': 'Particle Photon',
                'version': 'v1',
                'friendlyName': 'gatekeeper',
                'friendlyDescription': 'Gatekeeper connected via Particle Cloud',
                'isReachable': True,
                'actions': [
                    'turnOn'
                ],
                'additionalApplianceDetails': {}
            }
        ]
    }

    response = {
        'header': headers,
        'payload': payload,
    }

    logger.info("Returning discovery response: {}".format(json.dumps(response)))

    return response


def handle_turn_on_control(namespace, payload):
    logger.info('Handling control request.')

    # The OAuth2 access token for access to the Particle Cloud API.
    access_token = payload['accessToken']

    # The Particle device ID.
    device_id = payload['appliance']['applianceId']

    # Call the `prime` function on the device.
    url = PARTICLE_CLOUD_API_ENDPOINT + '/v1/devices/{}/prime'.format(device_id)
    response = requests.post(url, headers={
        'Authorization': 'Bearer ' + access_token,
    })

    logger.info("Response from Particle Cloud: {}".format(response.json()))

    headers = {
        'messageId': str(uuid.uuid4()),
        'name': 'TurnOnConfirmation',
        'namespace': namespace,
        'payloadVersion': '2',
    }

    response = {
        'header': headers,
        'payload': {},
    }

    logger.info("Returning control response: {}".format(json.dumps(response)))

    return response


def handle_health_check(namespace):
    logger.info('Handling health check request.')

    headers = {
        'messageId': str(uuid.uuid4()),
        'name': 'TurnOnConfirmation',
        'namespace': namespace,
        'payloadVersion': '2',
    }

    payload = {
        'description': 'Gatekeeper is probably online',
        'isHealthy': True,
    }

    response = {
        'header': headers,
        'payload': payload,
    }

    logger.info("Returning health check response: {}".format(json.dumps(response)))

    return response
