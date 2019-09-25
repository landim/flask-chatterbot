from flask import Flask, render_template, request
import http.client
import requests
import uuid
import urllib.parse
import redis
import json
from ibm_watson import AssistantV2
import ibm_watson
from ibm_watson import AssistantV2

app = Flask(__name__)

r = redis.Redis()

# Set up Assistant service.
service = AssistantV2(
    version='2019-02-28',
    iam_apikey='Kx0uMPQUZvuX_eJ4Az8BidiVIpF2d8TScSI3MfQxao59',
    url='https://gateway.watsonplatform.net/assistant/api'
)
service.disable_SSL_verification()

assistant_id = 'eb9e7b7d-b240-4f5a-a1bf-37813a9ca493'


sessions = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')

    return get_response(userText, 'web')

#9a00c6239ea8ef298c8862924d69f5855d790be83e7f0
#   {
#     "data": {
#       "type": "tickets",
#       "attributes": {
#         "nome-completo": "Mario Ricardo",
#         "conhecido-por": "Mario Ricardo",
#         "cpf": "963.440.033-75",
#         "data-nascimento": "1997-11-23",
#         "endereco": "Old Town Road",
#         "celular-whatsapp": "(19) 90026-4173",
#         "celular": "(77) 93463-0865",
#         "ativo": true,
#         "usuario_id": "4"
#       }
#     }
#   }

def get_response(text, contact_uid):
    try:
        # Invoke a Watson Assistant method

        session_id = service.create_session(
            assistant_id = assistant_id
        ).get_result()['session_id']
        sessions[contact_uid] = session_id

        message_input = {
            'message_type:': 'text',
            'text': ''
            }


        # Send message to assistant.
        response = service.message(
            assistant_id,
            session_id,
            input = message_input
        ).get_result()

        # If an intent was detected, print it to the console.
        if response['output']['intents']:
            print('Detected intent: #' + response['output']['intents'][0]['intent'])
            if (response['output']['intents'][0]['intent'] == "#create_ticket"):
                #start creating ticket...
                r.set(contact_uid, json.dumps({'text': ''}))
        else:
            #store text


        # Print the output from dialog, if any. Supports only a single
        # text response.
        if response['output']['generic']:
            if response['output']['generic'][0]['response_type'] == 'text':
                print(response['output']['generic'][0]['text'])

        # Prompt for next round of input.
        user_input = input('>> ')
        message_input = {
            'text': user_input
        }



    except ApiException as ex:
        print "Method failed with status code " + str(ex.code) + ": " + ex.message


    if (text.upper() == 'DOMO'):
        return 'Olá, sou Domo.\nEscolha uma das opções abaixo para eu te ajudar:\n*1 - Registrar um ticket*\n*2 - Reservar uma sala*'
    if (text.upper() == '1'):
        # todo create redis entry
        # todo create redis entry
        print(contact_uid)
        print(json.dumps({'text': ''}))
        r.set(contact_uid, json.dumps({'text': ''}))
        return 'Digite a sua ocorrência. Pode também enviar fotos e vídeos. Para finalizar, digite *FIM* ou *CANCELAR* para cancelar. :P'
    if (text.upper() == 'FIM'):
        obj_json = r.get(contact_uid)
        if (obj_json != None):
            ticket = json.loads(obj_json)
            r.delete(contact_uid)
            return 'Seu ticket foi cadastrado:\n' + ticket['text'] + '\n\nSeu ticket pode ser visualizado em www.elephantcoworking.com.br'
        else:
            return 'Nenhum ticket cadastrado'
    if (text.upper() == 'CANCELAR'):
        r.delete(contact_uid)
        return 'Cancelando cadastramento de ticket.'
    
    obj_json = r.get(contact_uid)
    if (obj_json != None):
        ticket = json.loads(obj_json)
        ticket['text'] = ticket['text'] + '\n' + text
        r.set(contact_uid, json.dumps(ticket))


    return None

@app.route("/whatsapp/receive", methods=['POST'])
def whatsapp_receive():
    print('================')
    print('Received :')
    event = request.form['event']
    print(event)
    direction = request.form['message[dir]']
    contact_uid = request.form['contact[uid]']
    contact_name = request.form['contact[name]']
    print(direction)
    print(contact_uid)
    print(contact_name)
    if (event == 'message' and direction == 'i' and (contact_name == 'Andre Buxexa' or contact_name == 'Rafa Elephant')):
        token = request.form['token']
        print(token)
        contact_uid = request.form['contact[uid]']
        text = request.form['message[body][text]']
        print(text)
        text_response = get_response(text, contact_uid)
        if (text_response != None):
            #connection = http.client.HTTPConnection('https://www.waboxapp.com/', 80, timeout=10)
            headers = {'Content-type': 'application/json'}

            query_params = {'token': '9a00c6239ea8ef298c8862924d69f5855d790be83e7f0',
                            'uid': '558581337181',
                            'to': contact_uid,
                            'custom_uid': str(uuid.uuid1()),
                            'text': text_response}
            url_params = urllib.parse.urlencode(query_params)
            print(url_params)

            response = requests.post('https://www.waboxapp.com/api/send/chat?' + url_params, headers=headers)
            print(response)            
            
    return str('worked!')


if __name__ == "__main__":
    app.run()
