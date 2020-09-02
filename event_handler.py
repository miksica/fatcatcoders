import requests
import pprint
import random
from flask import jsonify  # server stuff
import time
pp = pprint.PrettyPrinter(indent=4)

rndnms = [
    'Mihailo Miksa',
    'Markob',
    'Gandalf',
    'Leon',
    'Leki',
    'Hajduk',
    'Drej',
    'Dzonson',
    'Nina',
    'Ninja',
    'Dunja',
    'Braka',
    'Sone',
    'DZONI',
    'Pera',
    'MIka',
    'zika',
    'slikar069',
    'nikolica',
    'mikri',
    'eufrat',
    'zekenberg mark',
    'homer simpson',
    'boki',
    'rema',
    'ckelu'
]

lista_klijent_objectova = []
klijenti_webhookovi = {}
current_client = 0

urlsudojoin = 'http://127.0.0.42:5001/clientwebhook'
urlsudoattack = 'http://127.0.0.42:5001/clientwebhook'
urlsudoleave = 'http://127.0.0.42:5001/clientwebhook'


def error_json(msg):
    return jsonify({
        'status': 'Error!',
        'msg': msg
    })


def success_json(msg):
    return jsonify({
        'status': 'Success!',
        'msg': msg
    })


def next_webhook():
    global current_client
    current_client = current_client + 1
    return 'client' + str(current_client).zfill(5)


def novo_ime():
    ime = random.choice(rndnms)
    rndnms.remove(ime)
    return ime


class Client(object):
    
    def __init__(self, webhook='client00001', name='John Doe', squads=10):
        global lista_klijent_objectova
        self._webhook = webhook
        self._name = name
        self._squads = squads
        self._accesstoken = None

        self._log = {}

        lista_klijent_objectova.append(self)

    @staticmethod
    def ping_client_server():
        url = 'http://127.0.0.42:5001/'
        headers = {'Content-type': 'application/json'}
        ping = {
            'ArmyInfo': {
                'name': 'pingtest',
                'squads': '20'
            },
            'Webhook': ''
        }
        odg = requests.post(url, json=ping, headers=headers)
        print(odg.text)

    def mojaccesstoken(self):
        return self._accesstoken

    def mojeime(self):
        return self._name

    def set_access_token(self, token):
        self._accesstoken = token

    def set_webhook(self, webhook):
        self._webhook = webhook

    def daj_moj_webhook(self):
        return self._webhook

    def set_squads(self, squads='random'):
        if squads == 'random':
            self._squads = random.randint(10, 100)
        elif type(squads) == int and 100 >= int(squads) >= 10:
            self._squads = squads

    def add_log(self, msg):
        if msg.get('LogTime'):
            vreme_unosa = msg.get('LogTime')
            del msg['LogTime']
            self._log[vreme_unosa] = msg

    def daj_moj_log(self):
        sortirani_log = [{'LogBook': self._name}]
        for log in sorted(self._log):
            sortirani_log.append({log: self._log[log]})
        return sortirani_log

    def sudo_join(self, joinurl, newarmy=False):
        print('\n====1. Sending sudo JOIN to client Server=====')
        if self._webhook:
            joinurl += '/' + str(self._webhook)
        else:
            raise RuntimeError('Nemas self._webhook:')
        headers = {'Content-type': 'application/json'}

        acces_token = self._accesstoken
        # print('iz sudo joina')
        # print(acces_token)

        if newarmy:
            acces_token = ''
        # print(acces_token)

        sudojoinjson = {
            'ArmyInfo': {
                'name': self._name,
                'squads': self._squads
            },
            'Webhook': self._webhook,
            'sudo': 'join',
            'accessToken': acces_token
        }
        print(joinurl)

        odg = requests.post(joinurl, json=sudojoinjson, headers=headers)
        print(odg)
        print('\t==================================\n')

        return odg

    def sudo_attack(self, attackurl, who='random'):
        print('\n====2. Sending sudo ATTACK to client Server=====')
        if self._webhook:
            attackurl += '/' + str(self._webhook)
        else:
            raise RuntimeError('Nemas self._webhook:')
        headers = {'Content-type': 'application/json'}
        print(attackurl)
        print('sudo attack taktika {}'.format(who))
        acces_token = self._accesstoken if self._accesstoken else ''
        if not acces_token:
            return error_json('Ne mozes da napadas, jos uvek nemas [accessToken], prvo mora sudo JOIN'), 400
        # print('prosao token')
        sudoattackjson = {
            'sudo': 'attack',
            'attackWho': who
        }

        odg = requests.post(attackurl, json=sudoattackjson, headers=headers)
        print(odg)
        print('\t==================================\n')

        return odg

    def sudo_leave(self, leaveurl):
        print('\n====3. Sending sudo LEAVE to client Server=====')
        if self._webhook:
            leaveurl += '/' + str(self._webhook)
        else:
            raise RuntimeError('Nemas self._webhook:')
        headers = {'Content-type': 'application/json'}
        print(leaveurl)
        acces_token = self._accesstoken if self._accesstoken else ''

        if not acces_token:
            return error_json('Ne mozes da leavujes game, jos uvek nemas [accessToken], prvo mora sudo JOIN'), 400
        print('prosao token')

        sudoleavejson = {
            'sudo': 'leave',
        }

        odg = requests.post(leaveurl, json=sudoleavejson, headers=headers)
        print(odg)
        print('\t==================================\n')

        return odg


if __name__ == '__main__':

    '''
    event_handler.py hendluje sve zahteve klijenata
    funkcionise tako sto salje sudo komande na [client_server]
    koje onda server obradjuje i salje zahteve na pravi server
    "Ovo simulira prave kijente koji zahtevaju REST APIJE na glavni server"
    informacije se beleze samo kada ih server posalje nazad, kada je dobijena odgovarajuca povratna info
    event_handler provajduje webhookove, i generise ih redom client00001, client00002...
    kako je glavni server izvor svih istina to [client_server] samo zna ono sto bi klijenti znali
    a to je ko je na serveru i njihov log
    ovaj event_handler.py tehnicki ne zna nista, i sluzi samo za slanje komandi na klijent server
    u stvari zna, ali logove koje belezi su samo od return JSON od zahtevanih apija
    svi webhookovi se storuju na [client_server]-u u for klijent in lista_klijenata log = klijent['_log']
    '''

    ###############################
    # PRVI JOIN for in range ( max = len(rndnms) )
    ###############################
    for i in range(10):
        time.sleep(random.randint(0, 100)/200)  # delays execution by 0 to 0.5 seconds
        newclient = Client(webhook=next_webhook(), name=novo_ime(), squads=random.randint(10, 100))
        print('token posle kreacije')
        print(newclient.mojaccesstoken())
        # join server
        response = newclient.sudo_join(urlsudojoin)
        newclient.add_log(response.json())
        responsetoken = response.json().get('accessToken')
        newclient.set_access_token(responsetoken)
        print('token nakon responsa')
        print(newclient.mojaccesstoken())
        pp.pprint(response.json())

    ###############################
    # -- LEAVE --- 5 loopova da njih 5 random izadje
    ###############################
    for i in range(5):
        leaver = random.choice(lista_klijent_objectova)
        response = leaver.sudo_leave(urlsudoleave)
        print('status odgovora')
        print(response.status_code)
        print('response LEAVE')
        pp.pprint(response.json())

    ##############################
    # ONDA RE - JOIN za sve klijente da vidim da li razlikuje request kad je vec upisan
    ##############################
    for client in lista_klijent_objectova:
        time.sleep(random.randint(0, 100)/200)  # delays execution by 0to2 seconds
        print('==token vec postojeceg')
        print(client.mojaccesstoken())
        # join server
        response = client.sudo_join(urlsudojoin)
        client.add_log(response.json())
        # print('status odgovora')
        # print(response.status_code)
        responsetoken = response.json().get('accessToken')
        client.set_access_token(responsetoken)
        print('token nakon responsa')

        print(client.mojaccesstoken())
        pp.pprint(response.json())

    # ###############################
    # # -- LEAVE --- 5 loopova da njih 5 random izadje
    # ###############################
    # for i in range(5):
    #     leaver = random.choice(lista_klijent_objectova)
    #     response = leaver.sudo_leave(urlsudoleave)
    #     print('status odgovora')
    #     print(response.status_code)
    #     print('response LEAVE')
    #     pp.pprint(response.json())

    ##############################
    #  -- FAJT --- 10 loopova (ili koliko god) da klijenti napadaju. (salje i na webhokove vec izbacenih ljudi)
    ##############################
    for i in range(20):
        print('loop {}'.format(i))
        for client in lista_klijent_objectova:
            time.sleep(random.randint(0, 100)/200)  # delays execution by rand 0to2 seconds

            # attack som1 on server
            response = client.sudo_attack(urlsudoattack, who='random')  # who='random' / who='strongest'
            # client.add_log(response.json())
            print('status odgovora')
            print(response.status_code)
            print('response ATTACK')
            pp.pprint(response.json())
    #
    # ##############################
    # # RE JOIN opet kada su tokeni izbaceni iz baze
    # ##############################
    # print('REJKOIN posle kickovanih od napadanja')
    # for client in lista_klijent_objectova:
    #     time.sleep(random.randint(0, 100)/200)  # delays execution by 0to2 seconds
    #     # print('==token vec postojeceg')
    #     # print(client.mojaccesstoken())
    #     # join server
    #     response = client.sudo_join(urlsudojoin)
    #     client.add_log(response.json())
    #     # print('status odgovora')
    #     # print(response.status_code)
    #     responsetoken = response.json().get('accessToken')
    #     client.set_access_token(responsetoken)
    #     print('token nakon responsa')
    #
    #     print(newclient.mojaccesstoken())
    #     pp.pprint(response.json())
    #
    # ##############################
    # # -- FAJT --- 10 loopova (ili koliko god) da klijenti napadaju.
    # ##############################
    # for i in range(20):
    #     print('loop {}'.format(i))
    #     for client in lista_klijent_objectova:
    #         time.sleep(random.randint(0, 100)/200)  # delays execution by rand 0to2 seconds
    #
    #         # attack som1 on server
    #         response = client.sudo_attack(urlsudoattack, who='weakest')
    #         # client.add_log(response.json())
    #         print('status odgovora')
    #         print(response.status_code)
    #         print('response ATTACK')
    #         pp.pprint(response.json())

    # ###############################
    # # -- LEAVE --- 15 loopova da njih 15 random izadje
    # ###############################
    # for i in range(15):
    #     leaver = random.choice(lista_klijent_objectova)
    #     response = leaver.sudo_leave(urlsudoleave)
    #     print('status odgovora')
    #     print(response.status_code)
    #     print('response LEAVE')
    #     pp.pprint(response.json())
    #
    # for klijent in lista_klijent_objectova:
    #     print(klijent.mojaccesstoken())
    #     klijent.set_squads(15)
    #     response = klijent.sudo_join(urlsudojoin, newarmy=False)
    #     pp.pprint(response.json())
