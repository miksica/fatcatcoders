# run both servers than run event_handler.py

import os
ROOT_DIR = os.path.abspath(os.curdir)
MOJ_DIR = ROOT_DIR+'\miksa.Log'
import requests
import pprint
import random
from flask import Flask, request, jsonify  # server stuff
pp = pprint.PrettyPrinter(indent=4)

import logging

LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
logging.basicConfig(filename=MOJ_DIR,
                    level=logging.DEBUG,
                    format=LOG_FORMAT,
                    filemode='w')
logger = logging.getLogger()
logger.info('test msg')


defaultarmy = {
    'name': 'Default Army',
    'squads': 1
}

default_klijent_info = {
    'ArmyInfo': defaultarmy,
    'accessToken': '',
    'Webhook': '',
    '_Status': 200
}

# interna baza koja simulira razlicite klijente sa svojim statusima
lista_klijenata = []
'''
[lista_klijenata] sluzi kao interna baza klijenata
razlog postojanja je zapis webhook informacija koje dolaze od glavnog servera
evenet_handler.py u svojim funkcijama Clienta pinguje ovaj server
i on mu vraca logove, koji se onda merguju na event_+handleru 
   (prethodna recenica vise nije istina, jer nisam slao logove na event_handler.py 
   zbog webhooka koje server salje samo klijent serveru, znaci morali su ovde biti zabelezeni)
sve ovo radi adekvatnog testiranja kroz
   - pp.pprint(sredi_log_klijenta)
funkcija koja ispisuje ceo log klijenta sve joinove, leavove i attackove
Logovi se ispisuju kada se klijent kikckuje iz nekod od tri razloga

Da bi se pronasao log -> CTRL+F 'Sredjeni Log:' 

lista_klijenata = [
    {'ArmyInfo':{'name':_____,
                 'squads':_____},
     'accessToken':_______,  # u startu je '' ali server vraca token
     'Webhook':________,     # inicijalno providuje evend_handler.py ali vraca ga server i tada se upisuje kao validan
     '_Status': 200 / 400 / 404
     '_Log':{__pytztime___:____returnJSON___}
    }
]
'''

klijenti_webhookovi = {}
current_client = 0

urljoin = 'http://127.0.0.1:5000/api/join'
urlleave = 'http://127.0.0.1:5000/api/leave'
urlattack = 'http://127.0.0.1:5000/api/attack'


app = Flask(__name__)


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


def dodaj_u_log_klijenta(klijent_webhook, log):
    for klijent in lista_klijenata:
        if klijent_webhook == klijent['Webhook']:
            if log.get('LogTime'):
                vreme_unosa = log.get('LogTime')
                del log['LogTime']
                klijent['_Log'].append({vreme_unosa: log})


def sredi_log_klijenta(klijent):
    time_sorted_log = []
    for log in klijent['_Log']:
        for vreme_unosa in log:
            time_sorted_log.append(vreme_unosa)

    sredjeni_log = {}
    for unos in sorted(time_sorted_log):
        for log in klijent['_Log']:
            if unos in log:
                sredjeni_log[unos] = log[unos]
    return sredjeni_log


def ukloni_klijenta_iz_baze_po_webhooku(webhook):
    for klijent in lista_klijenata:
        if webhook == klijent['Webhook']:
            lista_klijenata.remove(klijent)


def set_status_po_klijent_webhooku(klijent_webhook, status):
    for klijent in lista_klijenata:
        if klijent_webhook == klijent['Webhook']:
            klijent['_Status'] = status


def daj_status_po_klijent_webhooku(webhook):
    for klijent in lista_klijenata:
        if webhook == klijent['Webhook']:
            status = klijent.get('_Status')
            return status


def set_access_token(klijent_webhook, access_token):
    for klijent in lista_klijenata:
        if klijent_webhook == klijent['Webhook']:
            klijent['accessToken'] = access_token


def daj_klijenta_po_webhooku(klijent_webhook):
    # print('dajem klijenta po webhooku')
    for klijent in lista_klijenata:
        # print('evo je lista klijenata po kojoj trazim')
        # print(lista_klijenata)
        # print('evo po cemu vrtim')
        # print(klijent)
        if klijent_webhook == klijent['Webhook']:
            # print('evo sta vracammmmmmm')
            # print(klijent)
            return klijent


def daj_klijenta_po_accesstokenu(klijent_access_code):
    for klijent in lista_klijenata:
        if klijent_access_code == klijent['accessToken']:
            return klijent


def daj_ime_klijenta_po_webhooku(trazeni_webhook):
    for klijent in lista_klijenata:
        if trazeni_webhook == klijent['Webhook']:
            ime_klijenta = klijent['ArmyInfo'].get('name')
            return ime_klijenta


def daj_token_po_webhooku(webhook):
    for klijent in lista_klijenata:
        if webhook == klijent['Webhook']:
            return klijent.get('accessToken')


def daj_token_za_napad(taktika_napada='', webhooknapadaca=''):
    klijent_za_napasti = None
    # if not taktika_napada:
    #     return error_json('Fja [daj_token_iz_baze]: Nisi mi dao taktitku napada')
    # if not webhooknapadaca:
    #     return error_json('Fja [daj_token_iz_baze]: Nisi mi dao webhook napadaca')
    if taktika_napada == 'random':  # TODO random
        for i in range(len(lista_klijenata)):
            klijent = random.choice(lista_klijenata)
            if klijent and str(klijent.get('Webhook')) != str(webhooknapadaca):
                # print('{} nije {}'.format(webhooknapadaca, klijent.get('Webhook')))
                # print('vracam {}'.format(klijent.get('accessToken')))
                return klijent.get('accessToken')

    elif taktika_napada == 'weakest':  # TODO weakest
        najmanje_squadova = 100
        for klijent in lista_klijenata:
            squadovi = klijent['ArmyInfo'].get('squads')
            if squadovi < najmanje_squadova and str(klijent.get('Webhook')) != str(webhooknapadaca):
                klijent_za_napasti = klijent
                najmanje_squadova = squadovi

        if klijent_za_napasti:
            # print('vracam {}'.format(klijent_za_napasti.get('accessToken')))
            return klijent_za_napasti.get('accessToken')

    elif taktika_napada == 'strongest':  # TODO strongest
        najvise_squadova = 1
        for klijent in lista_klijenata:
            squadovi = klijent['ArmyInfo'].get('squads')
            print('squadovi su {}'.format(squadovi))
            if squadovi > najvise_squadova and str(klijent.get('Webhook')) != str(webhooknapadaca):
                klijent_za_napasti = klijent
                najvise_squadova = squadovi

        if klijent_za_napasti:
            # print('vracam {}'.format(klijent_za_napasti.get('accessToken')))
            return klijent_za_napasti.get('accessToken')

    else:
        return 'losa taktika napada?'


##############################
# OUT FUNKCIJE KA MAIN SERVERU
##############################

def join_server(url, clientinfo=None):
    # print('fja [join_server]')
    # print(clientinfo)
    if not clientinfo:
        # print('Nemam clientinfo')
        clientinfo = default_klijent_info

    for rec in default_klijent_info:  # tester koji vrti po svim keyovima i pita dal moj unosni ima sve sto treba
        # print(rec)
        if rec not in clientinfo and rec is not '_Status':  # drugi uslov, exlude _Status+
            # print('Fja [join_server]: Nemas [{}] u poslatom JSON-u'.format(rec))
            return error_json('Nema [{}] u poslatom JSON-u'.format(rec)), 400

    # ucitavam podatke iz sudo POST JSON-a
    mojtoken = clientinfo.get('accessToken')
    name = clientinfo['ArmyInfo'].get('name')
    squads = clientinfo['ArmyInfo'].get('squads')
    webhook = clientinfo.get('Webhook')
    # print('ucitani mojtoken {}'.format(mojtoken))
    # print('ucitani Webhook {}'.format(webhook))
    # print('ucitani name {}'.format(name))
    # print('ucitani squads {}'.format(squads))

    print('====1. Joining [badcat_server] =====')
    if mojtoken:  # ako imam token onda se RE-JOINUJ, ovo server hendluje, ja samo menjam URL joina
        url += '?accessToken=' + str(mojtoken)
    headers = {'Content-Type': 'application/json'}
    print(url)

    # saljem striktno poslovni JSON sa minimalnim brojem informacija na server (ali sve sto treba)
    # hardcode unosni json

    join_json = {
        'ArmyInfo': {
            'name': name,
            'squads': squads
        },
        'Webhook': webhook
    }
    print(join_json)

    # posalji zahtev na serverr
    response = requests.post(url, json=join_json, headers=headers)

    # handle response 1 -> prvi put ubacen token
    if response.json().get('status') and response.json().get('msg').startswith('Ubacen token:'):
        odg = response.json()
        access_token_od_servera = odg.get('accessToken')
        vreme_unosa = odg.get('LogTime')
        del odg['LogTime']
        # del odg['LogTime']

        # hardcode unosni json
        login_json = {
            'ArmyInfo': {
                'name': name,
                'squads': squads
            },
            'Webhook': webhook,
            'accessToken': access_token_od_servera,
            '_Status': 200,
            '_Log': [{vreme_unosa: odg}]
        }

        # print('===log je sad')
        # print(login_json['_Log'])

        print('Ucaujem klijenta {} u listu klijenata'.format(name))
        lista_klijenata.append(login_json)
        # print('lista_klijenata je sad: ')
        # pp.pprint(lista_klijenata)  # ovo postane tedious jer ima veliki broj logova po klijentima

    # handle response 2 -> vec ga ima u bazi
    elif response.json().get('status') and response.json().get('msg').startswith('Token vec ubacen:'):
        current_client_webhook = response.json().get('Webhook')
        dodaj_u_log_klijenta(current_client_webhook, response.json())

    original_status_code = response.status_code
    return response.json(), original_status_code  # ovo vraca ka [event_handler.py]-u
    # inicijalna ideja je bila da se sve informacije obradjuju u klasi klijenta na event_handleru
    # ali je ta ideja pala u wodu zbog webhookova koji se vracaju samo do  Client_servera
    # te sam ih morao upisivati u log preko ovog servera u internu bazu [lista_klijenata]


def attack_server(url, who='random', webhooknapadaca=''):
    # print(clientinfo)
    if not webhooknapadaca:
        return {
                   'msg': 'Nisi prosledio webhook napadaca (iz nekog razloga)',
                   'status': 'Error!'
               }, 400

    # ucitavam podatke potrebne za Napad
    taktika_napada = who
    ime_napadaca = daj_ime_klijenta_po_webhooku(webhooknapadaca)

    # obradjujem napad - vracam metu
    token_za_napasti = daj_token_za_napad(taktika_napada=taktika_napada, webhooknapadaca=webhooknapadaca)
    if not token_za_napasti:
        msg = 'Nemam koga da napadnem, samo sam ja {} na serveru ostao - WINNER ura!'.format(ime_napadaca)
        return {
                   'msg': msg,
                   'status': 'Error!'
               }, 400

    print('ulazim u moj_token sa {}'.format(webhooknapadaca))
    moj_token = daj_token_po_webhooku(webhooknapadaca)
    if not moj_token:
        print('Sry bro, im already dead')
        return {
            'msg': 'Sudo Attack poslat na webhook lika koji je vec mrtav',
            'status': 'Error!'
               }, 404

    print('====2. Attack in [badcat_server] =====')
    if token_za_napasti:  # ako imam token onda ga napadam njega
        url += '/' + str(token_za_napasti) + '?accessToken=' + str(moj_token)
    headers = {'Content-Type': 'application/json'}  # fakticki mi ne treba nemam json ni u PUT ATTACKU
    # print('urlatatck posle joina {}'.format(url))
    # print('setovan status napadaca {} na 400'.format(daj_ime_klijenta_po_webhooku(webhooknapadaca)))
    print('urlattack')
    print(url)

    set_status_po_klijent_webhooku(webhooknapadaca, 400)  # TODO klijent nije available dok ne dobije odgovor od servera

    response = requests.put(url, headers=headers)

    set_status_po_klijent_webhooku(webhooknapadaca, 200)  # dobio response, set to ready
    # print('response fja [attack_serve]')
    # print(response.text)
    # print(response.json())
    if response.json().get('defenderPostStatus') == 'Mrtav':
        # print('Client: [attackserver]')
        mrtvi_defender = daj_klijenta_po_accesstokenu(token_za_napasti)
        ime_umrlog = daj_ime_klijenta_po_webhooku(token_za_napasti)
        print('mrtvi defender {}'.format(ime_umrlog))
        msg = 'Sredjeni Log: Kicked by DEATH [attackserver] - ' \
              'stigao mi je [defenderPostStatus="Mrtav"], log kickovanog je:'
        print(msg)
        superlog = sredi_log_klijenta(mrtvi_defender)
        logger.info(str(superlog))
        for key in superlog:
            logger.info(str(key) + '-' + str(superlog[key]))
        pp.pprint(sredi_log_klijenta(mrtvi_defender))
        lista_klijenata.remove(mrtvi_defender)

    # print('resposne nakon fje attack_sever u client serveru: {}'.format(response))
    # print('{} status je sada {}'.format(daj_ime_klijenta_po_webhooku(webhooknapadaca),
    #                                     daj_status_po_klijent_webhooku(webhooknapadaca)))
    original_status_code = response.status_code
    return response.json(), original_status_code


def leave_server(url, webhook):
    token_leavera = daj_token_po_webhooku(webhook)
    # print('token leavera: {}'.format(token_leavera))
    headers = {'Content-Type': 'application/json'}  # fakticki mi ne treba nemam json u PUT LEAVE

    if token_leavera:  # ako imam token onda ga napadam njega
        url += '?accessToken=' + str(token_leavera)
        print('urlleave')
        print(url)

    response = requests.put(url, headers=headers)
    # print('Response')
    # print(response)
    if response:  # TODO kada livuje set status to AFK, pa ako ga neko napadne ili mu stigne webhook onda tek kick
        # print(response.status_code)
        # print(daj_status_po_klijent_webhooku(webhook))
        set_status_po_klijent_webhooku(webhook, 404)  # dobio je potvrdnbu od servera da je livovao, set status to afk
        # print(daj_status_po_klijent_webhooku(webhook))

    original_status_code = response.status_code
    return response.json(), original_status_code


@app.route('/', methods=['GET', 'POST'])  # obican target na server
def ping():
    return success_json('Uspesno pingovano'), 200


######################
#        IN          #
######################
@app.route('/clientwebhook/<string:webhook>', methods=['POST'])
def clientwebhook(webhook):

    if webhook:
        print('Client server (@app.route(/clientwebhook/<string:webhook>)\n\twebhook klijenta je: ', end='')
        print(str(webhook))
    else:
        return error_json('clientwebhook izgleda kao: clientwebhook/client00001 ili client00042'), 400

    # Prvo Proveravam Da Li Je JSON
    if request.headers['Content-Type'] == 'application/json':
        ucitani_json = request.get_json()
        print('Client Server (@app.route/clientwebhook/<string:webhook>)\n\tucitani json: ' + str(ucitani_json))
    else:
        return error_json('Nisi Poslao JSON'), 400

    #######################
    # DAL JE RDY ZA KOMANDU
    #######################

    # if daj_klijenta_po_webhooku(webhook):
    #     print(daj_status_po_klijent_webhooku(webhook))
    #     if daj_status_po_klijent_webhooku(webhook) == 200:
    #         pass
    #     elif daj_status_po_klijent_webhooku(webhook) == 400:
    #         return error_json("Klijent nije rdy, his status is 400")
    #     elif daj_status_po_klijent_webhooku(webhook) == 404:
    #         return error_json("Klijent already left the game, his status is 404")

    #####################
    # prvo SUDO komande #  --- JOIN
    #####################
    if 'sudo' in ucitani_json and ucitani_json['sudo'] == 'join':
        # print('ovaj {} ucitani json je prosao if sudo in'.format(ucitani_json))

        _status_klijenta = daj_status_po_klijent_webhooku(webhook)
        # print('_status_klijenta pre joina'.format(_status_klijenta))

        response, original_status_code = join_server(urljoin, clientinfo=ucitani_json)

        _status_klijenta = daj_status_po_klijent_webhooku(webhook)
        # print('_status_klijenta posle joina'.format(_status_klijenta))
        if _status_klijenta == 404:
            set_status_po_klijent_webhooku(webhook, 200)  # joinovao se ili rejoinovao i vise nije afk iliti 404

        return jsonify(response), original_status_code

    #####################
    # prvo SUDO komande #  --- ATTACK
    #####################
    if 'sudo' in ucitani_json and ucitani_json['sudo'] == 'attack':
        if not daj_klijenta_po_webhooku(webhook):

            return error_json('Attack poslat na webhook:[{}], a ovaj like je vec kickovan iz baze'.format(webhook)), 404

        if daj_status_po_klijent_webhooku(webhook) == 400:
            ime = daj_ime_klijenta_po_webhooku(webhook)  # TODO ako muj je _Status = 400, znaci da je u tuci
            return error_json('Klijent {} jos napada ne moze da primi novi ATTACK REQUEST'.format(ime)), 400
        napadac = daj_klijenta_po_webhooku(webhook)
        if napadac and napadac['ArmyInfo'].get('squads') < 10:
            ime = daj_ime_klijenta_po_webhooku(webhook)
            squad = napadac['ArmyInfo'].get('squads')  # TODO ispod da li ima dovoljan broj za napad
            return error_json('Ne mogu da napadam, {} ima manje od 10 squadova, i to {}'.format(ime, squad)), 400

        # print('ovaj {} ucitani json je prosao if sudo in attack'.format(ucitani_json))
        # print('lista_klijenata je sad: ')

        # pp.pprint(lista_klijenata)
        who_to_attack = ucitani_json.get('attackWho')
        print('CLient: saljem takktiku u fju za npaad {}'.format(who_to_attack))
        who_to_attack = 'random' if not who_to_attack else who_to_attack  # ako je iz nekog razlog poslat los zahtev

        # zahtev na server
        response, original_status_code = attack_server(urlattack, who=who_to_attack, webhooknapadaca=webhook)

        # print('=======response posle sudo joina je')
        # print(response)
        return jsonify(response), original_status_code

    #####################
    # prvo SUDO komande #  --- LEAVE
    #####################
    if 'sudo' in ucitani_json and ucitani_json['sudo'] == 'leave':
        # chekc if alreadyu left
        moj_status = daj_status_po_klijent_webhooku(webhook)
        # print('status ovog klijenta pre sudo leave je {}'.format(moj_status))
        if moj_status == 404:
            ime = daj_ime_klijenta_po_webhooku(webhook)
            return error_json('{} je vec livovao gejm, duplirana sudo LEAVE komanda'.format(ime)), 404

        # print('wbhook leavera primljen od sudo leave {}'.format(webhook))
        _status_klijenta = daj_status_po_klijent_webhooku(webhook)

        if not _status_klijenta:
            return error_json('Na ovom webhooku:[{}] nema igraca'.format(webhook)), 404
        # print('_stauts_klijenta {}'.format(_status_klijenta))
        response, original_status_code = leave_server(urlleave, webhook)
        if response:
            set_status_po_klijent_webhooku(webhook, 404)  # dobio je pozitivnu info da je afk, i set status to afk
            _status_klijenta = daj_status_po_klijent_webhooku(webhook)
            # print('_status_klijenta posle leave komande je {}'.format(_status_klijenta))

        return jsonify(response), original_status_code

    ####################################################
    #   sada WEBHOOK handle #  --- JOIN
    ####################################################
    if 'status' in request.get_json() and request.get_json()['status'] == 'joinwebhook':
        # TODO ako nije u bazi aktivnih onda return 404 ili 404 dead
        klijent_target_webhooka = daj_klijenta_po_webhooku(webhook)
        ime = daj_ime_klijenta_po_webhooku(webhook)
        print('DING! JOIN WEBHOOK za {}'.format(ime))
        # print(request.get_json())

        if daj_status_po_klijent_webhooku(webhook) == 404:
            print('Sredjeni Log: Kicked by not resiving JOIN webhook, log kickovanog je:')
            pp.pprint(sredi_log_klijenta(klijent_target_webhooka))
            ukloni_klijenta_iz_baze_po_webhooku(webhook)
            return error_json('Klijent nije tu, livovao je gejm jos ranije, izbacujem ga iz battle-a'), 404

        klijent_target_webhooka = daj_klijenta_po_webhooku(webhook)
        if klijent_target_webhooka:
            print('======klijent_target_webhooka {}======'.format(webhook))
            # print(klijent_target_webhooka)
            ime_klijenta_webhooka = daj_ime_klijenta_po_webhooku(webhook)
            # print('ClientServer: Notification! (poslata na webhook {} za {})'.format(webhook, ime_klijenta_webhooka))
            # print('\t' + str(ucitani_json.get('msg')))

            dodaj_u_log_klijenta(webhook, ucitani_json)
            # print('novi log {}'.format(ime_klijenta_webhooka))
            # pp.pprint(klijent_target_webhooka.get('_Log'))
            return success_json('Primio sam Notifikaciju, no kick pls. By {}'.format(ime_klijenta_webhooka)), 200
        else:
            return error_json('Nemam klijenta na ovom webhooku'), 404  # ovo se dalje procesuira u kick sa server side

    ####################################################
    # sada WEBHOOK handle #  --- ATTACK
    ####################################################
    if 'status' in request.get_json() and request.get_json()['status'] == 'attackwebhook':
        ime_klijenta = daj_ime_klijenta_po_webhooku(webhook)
        print('DING! ATTTACK WEBHOOK za {}'.format(ime_klijenta))
        print(request.get_json())
        dodaj_u_log_klijenta(webhook, ucitani_json)

        if daj_status_po_klijent_webhooku(webhook) == 404:
            ukloni_klijenta_iz_baze_po_webhooku(webhook)
            return error_json('Klijent nije tu, livovao je gejm jos ranije, izbacujem ga iz battle-a'), 404
        else:
            return success_json('Primio sam Notifikaciju, no kick pls. By {}'.format(ime_klijenta)), 200

    ####################################################
    # sada WEBHOOK handle #  --- LEAVE
    ####################################################
    if 'status' in request.get_json() and request.get_json()['status'] == 'leavewebhook':
        klijent_target_webhooka = daj_klijenta_po_webhooku(webhook)
        # TODO ako nije u bazi aktivnih onda return 404 ili 404 dead
        if daj_status_po_klijent_webhooku(webhook) == 404:
            ukloni_klijenta_iz_baze_po_webhooku(webhook)
            print('Sredjeni Log: Kicked by not resiving LEAVE webhook, log kickovanog je:')
            pp.pprint(sredi_log_klijenta(klijent_target_webhooka))
            return error_json('Klijent nije tu, livovao je gejm jos ranije, izbacujem ga iz battle-a'), 404

        if klijent_target_webhooka:
            # print('======klijent_leave_webhooka {}======'.format(webhook))
            # print(klijent_target_webhooka)
            ime_klijenta_webhooka = daj_ime_klijenta_po_webhooku(webhook)
            # print('ClientServer: Notification! (poslata na webhook {} za {})'.format(webhook, ime_klijenta_webhooka))
            # print('\t' + str(ucitani_json.get('msg')))

            dodaj_u_log_klijenta(webhook, ucitani_json)

            msg = 'Primio sam Notifikaciju da je {}, no kick pls. By {}'.format(
                request.get_json().get('msg'),
                ime_klijenta_webhooka
            )
            return success_json(msg), 200
        else:
            return error_json('Nemam klijenta na ovom webhooku'), 404


if __name__ == '__main__':
    app.run(host='127.0.0.42', port=5001, debug=True)
