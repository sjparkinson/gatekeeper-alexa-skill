import json
import logging
import requests
import uuid

PARTICLE_CLOUD_API_ENDPOINT = 'https://api.particle.io'
PARTICLE_CLOUD_AUTH_TOKEN = '@@PARTICLE_CLOUD_AUTH_TOKEN@@'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# Main function entrypoint, handles request routing.
def lambda_handler(event, context):
    logger.info("Recieved event: {}".format(json.dumps(event)))

    # The Smart Home API request namespace.
    namespace = event['header']['namespace']

    if namespace == 'Alexa.ConnectedHome.Discovery':
        return handle_device_discovery(namespace, event['payload'])

    if namespace == 'Alexa.ConnectedHome.Control':
        if event['header']['name'] == 'TurnOnRequest':
            return handle_turn_on_control(namespace, event['payload'])


def handle_device_discovery(namespace, payload):
    logger.info('Handling discovery event.')

    headers = {
        'messageId': str(uuid.uuid4()),
        'name': 'DiscoverAppliancesResponse',
        'namespace': namespace,
        'payloadVersion': '2',
    }

    # Call the `prime` function on the device.
    url = PARTICLE_CLOUD_API_ENDPOINT + '/v1/devices/20003a000747343232363230' # Yea it's hardcoded.
    device_info = requests.get(url, headers={
        'Authorization': 'Bearer ' + PARTICLE_CLOUD_AUTH_TOKEN,
    }).json()

    # Particle cloud is having issues.
    if response.status_code != 200:
        return {
            'header': {
                'messageId': str(uuid.uuid4()),
                'name': 'DependentServiceUnavailableError',
                'namespace': namespace,
                'payloadVersion': '2',
            },
            'payload': {
                'dependentServiceName': 'Particle Cloud'
            }
        }

    payload = {
        'discoveredAppliances': [
            {
                'applianceId': device_info['id'],
                'manufacturerName': 'Particle Industries, Inc.',
                'modelName': 'Particle Photon',
                'version': 'v1',
                'friendlyName': device_info['name'],
                'friendlyDescription': 'Gatekeeper connected via Particle Cloud',
                'isReachable': device_info['connected'],
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

    # The Particle device ID.
    device_id = payload['appliance']['applianceId']

    # Call the `prime` function on the device.
    url = PARTICLE_CLOUD_API_ENDPOINT + '/v1/devices/{}/prime'.format(device_id)
    response = requests.post(url, headers={
        'Authorization': 'Bearer ' + PARTICLE_CLOUD_AUTH_TOKEN,
    })

    logger.info("Response from Particle Cloud: {}".format(response.json()))

    # Particle cloud is having issues.
    if response.status_code != 200:
        return {
            'header': {
                'messageId': str(uuid.uuid4()),
                'name': 'DependentServiceUnavailableError',
                'namespace': namespace,
                'payloadVersion': '2',
            },
            'payload': {
                'dependentServiceName': 'Particle Cloud'
            }
        }

    # The door is already open.
    if response.json()['return_value'] != 0:
        return {
            'header': {
                'messageId': str(uuid.uuid4()),
                'name': 'NotSupportedInCurrentModeError',
                'namespace': namespace,
                'payloadVersion': '2',
            },
            'payload': {
                'currentDeviceMode': 'OTHER'
            }
        }

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
