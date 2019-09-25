# Example 2: adds user input and detects intents.

import ibm_watson
from ibm_watson import AssistantV2
from pprint import pprint
import json

# Set up Assistant service.
service = AssistantV2(
    version='2019-02-28',
    iam_apikey='Kx0uMPQUZvuX_eJ4Az8BidiVIpF2d8TScSI3MfQxao59',
    url='https://gateway.watsonplatform.net/assistant/api'
)
service.disable_SSL_verification()

assistant_id = 'eb9e7b7d-b240-4f5a-a1bf-37813a9ca493'

# Create session.
session_id = service.create_session(
    assistant_id = assistant_id
).get_result()['session_id']

# Initialize with empty value to start the conversation.
message_input = {
    'message_type': 'text',
    'text': '',
    'options': {
            'return_context': True
        }
    }

# Main input/output loop
while message_input['text'] != 'quit':

    # Send message to assistant.
    response = service.message(
        assistant_id,
        session_id,
        input = message_input
    ).get_result()


    # If an intent was detected, print it to the console.
    if response['output']['intents']:
        print('Detected intent: #' + response['output']['intents'][0]['intent'])
    
    print(json.dumps(response, indent=2))

    # Print the output from dialog, if any. Supports only a single
    # text response.
    if response['output']['generic']:
        if response['output']['generic'][0]['response_type'] == 'text':
            print(response['output']['generic'][0]['text'])

    # Prompt for next round of input.
    user_input = input('>> ')
    message_input = {
        'text': user_input,
        'options': {
            'return_context': True
        }
    }

# We're done, so we delete the session.
service.delete_session(
    assistant_id = assistant_id,
    session_id = session_id
)

