# run both servers than run event_handler.py

from flask import Flask, request, jsonify  # server stuff
import requests
import os
from datetime import datetime
import pprint  # za debuging purposes
import binascii  # za random token
import pytz  # za vreme
import datetime  # za pytz
import time  # za sleep servera na attack api
import random
import math

import mysql.connector
# 0 MYSQL #
###########

mydb = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='ba na na',
    database='main_db'  # na prvi run runovati bez ove linije?
)


def postavi_bazu():
    mycursor = mydb.cursor()
    mycursor.execute('DROP TABLE IF EXISTS main_table')  # resetuj db_table
    mycursor.execute('CREATE DATABASE IF NOT EXISTS main_db')  # napravi DB
    mycursor.execute(
        'CREATE TABLE IF NOT EXISTS main_table ('
        'accessToken VARCHAR(255) PRIMARY KEY NOT NULL,'
        'name VARCHAR(255),'
        'squad INTEGER(3),'
        'webhook VARCHAR(255))'
        'ENGINE=InnoDB DEFAULT CHARSET=utf8'
    )


def ubaci_u_bazu_novog_lika(novi_lik):
    ime = novi_lik.get('name')
    token = novi_lik.get('accessToken')
    webhook = novi_lik.get('Webhook')
    squads = novi_lik.get('squads')
    mycursor = mydb.cursor()

    unos = 'INSERT INTO main_table (accessToken, name, squad, webhook) VALUES (%s, %s, %s, %s)'
    podaci = (token, ime, squads, webhook)

    mycursor.execute(unos, podaci)
    mydb.commit()


def daj_lika_iz_db_po_tokenu(token):
    mycursor = mydb.cursor()

    unos = 'SELECT * FROM main_table WHERE accessToken = %s'
    token_tapl = (token, )
    mycursor.execute(unos, token_tapl)
    rezultat = mycursor.fetchone()
    return rezultat


def obrisi_lika_iz_db_po_tokenu(token):
    mycursor = mydb.cursor()

    unos = 'DELETE FROM main_table WHERE accessToken =%s'
    token_tapl = (token, )
    mycursor.execute(unos, token_tapl)


def set_squads_of_lik_in_db_po_tokenu(token, novo_stanje):
    mycursor = mydb.cursor()
    unos = 'UPDATE main_table SET squad =%s WHERE accessToken =%s'
    token_tapl = (novo_stanje, token)
    mycursor.execute(unos, token_tapl)


# 0 Default Variable ####################
#########################################
pp = pprint.PrettyPrinter(indent=4)

app = Flask(__name__)
webhook_base_url = 'http://127.0.0.42:5001/clientwebhook'

# interna baza
lista_autorizovanih_tokena = []
lista_webhook_urlova = []
dict_token_armyinfo = {}
dict_token_webhook = {}
glavna_baza = []
'''
[glavna_baza] sluzi kao interna baza klijenata


glavna_baza = [
    {
     'name':____
     'squads':_____,
     'accessToken':_______,  # u startu je '' ali server vraca token
     'Webhook':________,     # providuje evend_handler ali vraca ga server tada se upisuje kao validan
    }
]
'''
# glavna_baza_kolone = {
#         'name': '',
#         'squads': '',
#         'accessToken': '',
#         'Webhook': ''
# }


# defaulti
defaultarmy = {
    'name': 'Default Army',
    'squads': 1
}

defaultheaderi = {'Content-Type': 'application/json'}


# 1 Funkcije Servera ####################
#########################################
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


def trenutno_vreme():
    vreme_je = pytz.utc.localize(datetime.datetime.now())
    # print(vreme_je)
    # print(str(vreme_je))
    return str(vreme_je)


def random_token():  # random token generator
    temp_token = binascii.hexlify(os.urandom(10))
    return temp_token.decode('utf-8')  # ed08178df6af9f9e6cbc


# low level funkcije sa pocetka
# def dajsvaimenanaserveru():
#     listaimena = []
#     for key in dict_token_armyinfo:
#         listaimena.append(dict_token_armyinfo.get(key))
#     return listaimena
#
#
# def dajimetokena(token):
#     return dict_token_armyinfo.get(token)
#
#
# def army_join_webhook(json_joinovanog):
#     for webhookurl in lista_webhook_urlova:
#         requests.put(webhookurl, json=json_joinovanog, headers=defaultheaderi)


# iste fje ko sa klijent servera 
# ##############################
def set_access_token(klijent_webhook, access_token):
    for klijent in glavna_baza:
        if klijent_webhook == klijent['Webhook']:
            klijent['accessToken'] = access_token


def daj_klijenta_po_webhooku(klijent_webhook):
    for klijent in glavna_baza:
        if klijent_webhook == klijent['Webhook']:
            return klijent


def daj_klijenta_po_accesstokenu(klijent_access_code):
    for klijent in glavna_baza:
        if klijent_access_code == klijent['accessToken']:
            return klijent


def daj_autorizovane_tokene():
    tokeni_za_vratiti = []
    for klijent in glavna_baza:
        tokeni_za_vratiti.append(klijent['accessToken'])
    return tokeni_za_vratiti


def obradi_napad(napadac_tapl, defender_tapl):

    napadac_token, napadac_name, napadac_squad, napadac_webhook = napadac_tapl
    defender_token, defender_name, defender_squad, defender_webhook = defender_tapl

    print('attacker_klijent je {}'.format(napadac_name))
    print('defender_klijent je {}'.format(defender_name))

    attacker_squads = napadac_squad
    defender_squads = defender_squad

    chance_to_hit = round(100/attacker_squads, 2)  # TODO Attack chances
    evasion = 100 - defender_squads  # TODO Received damage

    print('chance to hit {}'.format(chance_to_hit))
    print('evasion to hit {}'.format(evasion))

    for i in range(attacker_squads):  # TODO Repeat attack
        time_to_reload = math.floor(attacker_squads/10)
        max_damage = int(round(attacker_squads / (i + 1)))  # TODO Squads over Repeats
        vreme_sad = trenutno_vreme()

        # uracunavam i decimale u to hit, jer mi je bitno zbog mnozenja da uvek bude oko ili vise od %99.6
        if round(random.randint(1, 10000)/100, 2) <= chance_to_hit:  # ROLL TO HIT
            if random.randint(1, 100) <= evasion:  # ROLL TO EVADE (half damage)
                reduced_dmg = int(math.floor(max_damage/2))  # --------------  EVADED
                # ovo je okej jer 1 dmg nece ubiti 1 lika, ali 2 dmga hoce ubiti cak iako evaduje
                # a flor je okej jer ako uradimo 15,5 dmga, ubicemo samo 15 likova
                # ovako kiled suqads = dmg done
                evasion_status = 'Succesful Evasion, will recieve half dmg, {} from {}'.format(reduced_dmg, max_damage)
                dmg_done = reduced_dmg + 15  # todo povecan dmg zbog testiranja
            else:
                evasion_status = 'Fail, he will hit for full dmg {}'.format(max_damage)
                dmg_done = max_damage + 15  # todo povecan dmg zbog testiranja

            return {
                'status': 'Success!',
                'msg': 'Napad obavljen uspesno',
                'Napadac': napadac_name,
                'NapadacSquads': napadac_squad,
                'Defender': defender_name,
                'DefenderSquads': defender_squad,
                'chance_to_hit': chance_to_hit,
                'evasion': evasion,
                'evasionStatus': evasion_status,
                'maxdmg': attacker_squads,
                'dmgDone': dmg_done,
                'BattleLog': '{} je napao {} i ubio mu/joj {} squadova'.format(
                    napadac_name, defender_name, dmg_done
                ),
                'LogTime': vreme_sad
            }
        # else:  # ---------------  ROLL AGAIN

        time.sleep(time_to_reload/1000)  # TODO Reload time #hiljadu puta brze zbog testinga
        print('{} napad - "cekao sam" {} sekundi'.format(i + 1, time_to_reload))

    vreme_sad = trenutno_vreme()

    # ---------------   MISS
    print('Attack miss')
    return {
        'status': 'Success!',
        'msg': 'Napad obavljen neuspesno, Promasili smo sve udarce',
        'Napadac': napadac_name,
        'NapadacSquads': napadac_squad,
        'Defender': defender_name,
        'DefenderSquads': defender_squad,
        'chance_to_hit': chance_to_hit,
        'evasion': evasion,
        'evasionStatus': 'Not needed, he missed',
        'maxdmg': attacker_squads,
        'dmgDone': 0,
        'BattleLog': '{} je napao {} i ubio mu/joj {} squadova'.format(
            napadac_name, defender_name, 0
        ),
        'LogTime': vreme_sad
    }
#####################################################################################


def posaljisvima_joinwebhok(novilik, rejoin=False):
    name = novilik.get('name')
    squads = novilik.get('squads')
    webhook_novoglika = novilik.get('Webhook')

    sta = 'joined' if not rejoin else 'REjoined'
    for klijent in glavna_baza:
        klijent_webhook = klijent['Webhook']
        klijent_accesstoken = klijent['accessToken']
        if klijent_webhook is not webhook_novoglika:  # nemoj sam sebi da saljes
            vremesad = trenutno_vreme()
            print('Fja [posaljisvima_joinwebhok] vreme trenutno' + str(vremesad))
            headers = {'Content-Type': 'application/json'}
            webhook_url = webhook_base_url + '/' + str(klijent_webhook)
            webhook_msg = {
                'status': 'joinwebhook',
                'LogTime': vremesad,
                'msg': '{} {} game with {} squads'.format(name, sta, squads)
            }
            # print('radi url {}'.format(webhook_url))
            # print('saljem {}'.format(webhook_msg))
            response = requests.post(webhook_url, json=webhook_msg, headers=headers)

            if response.status_code == 404:
                glavna_baza.remove(klijent)
                obrisi_lika_iz_db_po_tokenu(klijent_accesstoken)
                print('Fja [posaljisvima_joinwebhok]: Ping 404 - uklanjam {} iz baze podataka'.format(klijent))
                print('Fja [posaljisvima_joinwebhok]: preostali na bazi')
                pp.pprint(glavna_baza)
            else:
                print(response.json())
                print('\tObavesten {} o dolasku {} na server sa {} squadova'.format(klijent_webhook, name, squads))


def posaljinapadnutom_attackwebhook(token_defendera, token_napadaca, broj_mrtvih_squadova, post_status):
    defender = daj_klijenta_po_accesstokenu(token_defendera)
    napadac = daj_klijenta_po_accesstokenu(token_napadaca)

    ime_napadaca = napadac.get('name')
    ime_defendera = defender.get('name')

    webhook_defendera = defender.get('Webhook')

    if webhook_defendera:
        vremesad = trenutno_vreme()
        print('Fja [posaljinapadnutom_attackwebhook] - vreme trenutno: ' + str(vremesad))
        headers = {'Content-Type': 'application/json'}
        webhook_url = webhook_base_url + '/' + str(webhook_defendera)
        webhook_msg = {
            'status': 'attackwebhook',
            'LogTime': vremesad,
            'msg': '{} te je napao i ubio {} squads'.format(ime_napadaca, broj_mrtvih_squadova),
            'defenderPostStatus': post_status
        }
        # print('radi url {}'.format(webhook_url))
        # print('saljem {}'.format(webhook_msg))
        response = requests.post(webhook_url, json=webhook_msg, headers=headers)
        print('Server: [posaljinapadnutom_attackwebhook]:')
        print(response.json())
        if response.status_code == 404:
            glavna_baza.remove(defender)
            try:
                obrisi_lika_iz_db_po_tokenu(token_napadaca)
            except RuntimeError('Evo me u eroru [posaljinapadnutom_attackwebhook]'):
                print('Evo me u eroru [posaljinapadnutom_attackwebhook]')
            else:
                mydb.commit()
            print('Fja [posaljisvima_joinwebhok]: Ping 404 - uklanjam {} iz baze podataka'.format(defender))
            print('Fja [posaljisvima_joinwebhok]: preostali na bazi')
            pp.pprint(glavna_baza)
        else:
            print(response.json())
            print('\tObavesten {} o napadu '.format(ime_defendera))


def posaljinapadacu_attackwebhook(token_defendera, token_napadaca, broj_mrtvih_squadova, post_status):
    defender = daj_klijenta_po_accesstokenu(token_defendera)
    napadac = daj_klijenta_po_accesstokenu(token_napadaca)

    ime_defendera = defender.get('name')

    webhok_napadaca = napadac.get('Webhook')

    if webhok_napadaca:
        vremesad = trenutno_vreme()
        print('Fja [posaljinapadnutom_attackwebhook] - vreme trenutno: ' + str(vremesad))
        headers = {'Content-Type': 'application/json'}
        webhook_url = webhook_base_url + '/' + str(webhok_napadaca)
        webhook_msg = {
            'status': 'attackwebhook',
            'LogTime': vremesad,
            'msg': 'Napali smo:{}, i ubili mu {} squads'.format(ime_defendera, broj_mrtvih_squadova),
            'defenderPostStatus': str(ime_defendera) + ' je ' + str(post_status)
        }

        # print('radi url {}'.format(webhook_url))
        # print('saljem {}'.format(webhook_msg))
        response = requests.post(webhook_url, json=webhook_msg, headers=headers)
        print('Server: [posaljinapadacu_attackwebhook]:')
        print(response.json())
        if response.status_code == 404:
            glavna_baza.remove(napadac)
            try:
                obrisi_lika_iz_db_po_tokenu(token_napadaca)
            except RuntimeError('Evo me u eroru [posaljinapadacu_attackwebhook]'):
                print('Evo me u eroru [posaljinapadacu_attackwebhook]')
            else:
                mydb.commit()
            print('Fja [posaljisvima_joinwebhok]: Ping 404 - uklanjam {} iz baze podataka'.format(napadac))
            print('Fja [posaljisvima_joinwebhok]: preostali na bazi')
            pp.pprint(glavna_baza)
        else:
            print(response.json())
            print('\tObavesten {} o napadu '.format(ime_defendera))


def posaljisvima_leavewebhook(token_leavera, mrtav=False):
    liver = daj_klijenta_po_accesstokenu(token_leavera)
    ime_leavera = liver['name']

    vremesad = trenutno_vreme()
    print('Fja [posaljisvima_leavewebhook] - vreme trenutno: ' + str(vremesad))
    headers = {'Content-Type': 'application/json'}
    if mrtav:
        msg = 'je Mrtav'
    else:
        msg = 'je otisao afk'

    for klijent in glavna_baza:
        if klijent['Webhook'] is not liver['Webhook']:
            webhook_to_send_leave = klijent['Webhook']
            webhook_url = webhook_base_url + '/' + str(webhook_to_send_leave)
            webhook_msg = {
                'status': 'leavewebhook',
                'LogTime': vremesad,
                'msg': '{} je {}'.format(ime_leavera, msg)
            }
            # print('radi url {}'.format(webhook_url))
            # print('saljem {}'.format(webhook_msg))
            response = requests.post(webhook_url, json=webhook_msg, headers=headers)
            print('Server: [posaljisvima_leavewebhook]:')
            print(response.json())

            token_na_koji_saljem = klijent['accessToken']

            if response.status_code == 404:
                glavna_baza.remove(klijent)
                try:
                    obrisi_lika_iz_db_po_tokenu(token_na_koji_saljem)
                except RuntimeError('Evo me u eroru [posaljisvima_leavewebhook]'):
                    print('Evo me u eroru [posaljisvima_leavewebhook]')
                else:
                    mydb.commit()
                print('Fja [posaljisvima_leavewebhook]: Ping 404 - uklanjam {} iz baze podataka'.format(klijent))
                print('Fja [posaljisvima_leavewebhook]: preostali na bazi')
                pp.pprint(glavna_baza)
            else:
                print('\tObavesten {} o leavu {} sa servera'.format(webhook_to_send_leave, ime_leavera))


# 2 Server API Routes ####### JOIN ######
#########################################
@app.route('/api/join', methods=['POST'])
def api_join():
    print('ucitani token je')
    print(request.args.get('accessToken'))
    # prvo proveravam token nevezano od ostalog iz urla
    if request.args.get('accessToken'):
        ucitani_token = request.args.get('accessToken')
        # ucitana_vojska = dict_token_armyinfo[ucitani_token] if ucitani_token in dict_token_armyinfo else erorvojska
        print('=== ZA JOIN ===')
        print('ekstraktovan token: ', end='')
        print(ucitani_token)
    else:
        ucitani_token = None
        # ucitana_vojska = None

    # onda dal je JSON
    if request.headers['Content-Type'] == 'application/json':
        ucitani_json = request.get_json()
        # if ucitani_json.get('squads') and ucitani_json.get('name'):
        #     posaljisvima_joinwebhok(ucitani_json)

    else:
        return error_json('Primamo samo JSON kao data Package'), 400

    # onda da li su mi poslali validan JSON
    if 'ArmyInfo' not in ucitani_json:
        return error_json('Nemas glavni podatak u JSONU -> [ArmyInfo]'), 400
    if 'Webhook' not in ucitani_json:
        return error_json('Nemas glavni podatak u JSONU -> [Webhook]'), 400
    for rec in defaultarmy:
        if rec not in ucitani_json['ArmyInfo']:
            return error_json('Nedostaje ti [{}] u [ArmyInfo]'.format(rec)), 400

    # print('ucitani token za join:'.format(ucitani_token))

    dal_si_u_bazi = daj_lika_iz_db_po_tokenu(ucitani_token)

    if dal_si_u_bazi:
        token_db, name_db, squad_db, webhook_db = daj_lika_iz_db_po_tokenu(ucitani_token)
    else:
        token_db = None
        name_db = None
        squad_db = None
        webhook_db = None

    if token_db and name_db and squad_db and webhook_db:
        print('Token vec ubacen:{} u glavnoj bazi'.format(token_db))

        # TODO DB dajinfopotokenu
        rejoin_lik = {
            'name': name_db,
            'squads': squad_db,
            'Webhook': webhook_db,
            'accessToken': token_db
        }
        posaljisvima_joinwebhok(rejoin_lik, rejoin=True)

        return jsonify({  # TODO "Dobrodosao nazad"
            'status': 'Success!',
            'msg': 'Token vec ubacen:[{}] u bazu, dobrodosao nazad {}'.format(token_db, name_db),
            'accessToken': ucitani_token,
            'squads': squad_db  # treba mi zbog ponovnog joinovanja jer default fja upisuje token
        }), 201

    else:  # ako nemam token treba da ga napravim i posaljem klijentu
        try:
            novi_token = random_token()
            lista_autorizovanih_tokena.append(novi_token)
            print('Server: UCITANI JSON', end='\n\t')
            print(ucitani_json)

            ucitana_vojska = ucitani_json['ArmyInfo']  # if 'ArmyInfo' in ucitani_json else defaultarmy, checkd
            dict_token_armyinfo[novi_token] = ucitana_vojska
            webhook = ucitani_json['Webhook']
            dict_token_webhook[novi_token] = webhook

            novi_lik_na_serveru = {
                'accessToken': novi_token,
                'name': ucitani_json['ArmyInfo'].get('name'),
                'squads': ucitani_json['ArmyInfo'].get('squads'),
                'Webhook': webhook
            }

            # zbog ovoga try
            # TODO FJA-1 Upisi ga u bazu
            ubaci_u_bazu_novog_lika(novi_lik_na_serveru)

            glavna_baza.append(novi_lik_na_serveru)  # TODO Ovo Obrisati kad proradi baza

            print('Server: Dodelio sam mu token:{} i ubacio u listu autorizovanih tokena'.format(novi_token))
            print('Server: Saljem svima webhook')

            # TODO FJA-4 Webhook poslati svima info
            posaljisvima_joinwebhok(novi_lik_na_serveru)

            vremesad = trenutno_vreme()

        except RuntimeError:
            mydb.rollback()
            return error_json('nije mogao da ubaci [token:{}] u bazu'.format(ucitani_token)), 400

        else:
            mydb.commit()
            return jsonify({
                'status': 'Success!',
                'msg': 'Ubacen token:[{}] u bazu'.format(novi_token),
                'accessToken': novi_token,
                'ArmyInfo': ucitana_vojska,
                'Webhook': webhook,
                'LogTime': vremesad
                # '_ListaTokena': lista_autorizovanih_tokena,
                # '_SpisakImena': dajsvaimenanaserveru(),
                # '_VezaTokenIme': dict_token_armyinfo
            }), 200


# 2.1 Server API Routes ##### ATTACK ####
#########################################
@app.route('/api/attack/<string:napadninjegatoken>', methods=['PUT'])
def api_attack(napadninjegatoken):
    print('STIGO ATTACK API')
    if napadninjegatoken:
        print('Server: Token koga treba napasti: {}'.format(napadninjegatoken))
    else:
        print("NEMA [napadninjegatoken] u zahtevu ATTACK APIJA")
        return error_json(
            'los zahtev za Attack, nedostaje ti napadninjegatoken u /api/attack/<string:napadninjegatoken>'
        ), 400

    # Prvo proveravam token nevezano od ostalog
    if request.args.get('accessToken'):
        token_napadaca = request.args.get('accessToken')
        print('=== ZA ATTACK ===')
        print('ekstraktovan token napadaca: ', end='')
        print(token_napadaca)
    else:
        return error_json('Ne moze ATTACK komanda bez accessToken-a'), 401

    # i onda dal imam tog lika [napadninjegatoken] u bazi

    defender_iz_baze = daj_lika_iz_db_po_tokenu(napadninjegatoken)
    attacker_iz_baze = daj_lika_iz_db_po_tokenu(token_napadaca)

    if defender_iz_baze:
        token_db_def, name_db_def, squad_db_def, webhook_db_def = daj_lika_iz_db_po_tokenu(napadninjegatoken)
    else:
        return error_json('igrac sa tokenom {} (Defender) not found or dead army'.format(napadninjegatoken)), 404

    if attacker_iz_baze:
        token_db_att, name_db_att, squad_db_att, webhook_db_att = daj_lika_iz_db_po_tokenu(napadninjegatoken)
        print('tu sam {}'.format(name_db_att))
    else:
        return error_json('igrac sa tokenom {} (Attacker) not found or dead army'.format(token_napadaca)), 404

    if token_db_def:
        # if daj_klijenta_po_accesstokenu(napadninjegatoken):
        defender_klijent = daj_klijenta_po_accesstokenu(napadninjegatoken)

        # print('Token Defendera: ' + str(napadninjegatoken))
        # print('======= FAJT =======')
        # napadac = dict_token_armyinfo.get(token_napadaca)
        # pp.pprint(napadac)
        # print('======== VS ========')
        # defender = dict_token_armyinfo.get(napadninjegatoken)
        # pp.pprint(defender)

        # TODO funkcija obradi_napad
        battle_info = obradi_napad(attacker_iz_baze, defender_iz_baze)
        print('battle_info je {}'.format(battle_info))

        # if battle_info['status'] == '404':  # nisam nasao koga da napadnem
        #     return error_json('igrac sa tokenom {} not found or dead army'.format(napadninjegatoken)), 404
        #     # TODO izbaci ga iz baze

        if battle_info.get('dmgDone') >= battle_info.get('DefenderSquads'):
            print('uklonio sam {} iz baze jer je mrtav'.format(defender_klijent.get('name')))
            battle_info['defenderPostStatus'] = 'Mrtav'

        else:
            preostali_squadovi = int(battle_info.get('DefenderSquads')) - int(battle_info.get('dmgDone'))
            battle_info['defenderPostStatus'] = 'Preziveo sa {} squadova'.format(preostali_squadovi)
            print('smanjio sam {} squadove sa {} na {}'.format(
                name_db_def,
                squad_db_def,
                preostali_squadovi
            ))
            # TODO Update info in DB
            try:
                set_squads_of_lik_in_db_po_tokenu(napadninjegatoken, preostali_squadovi)
            except RuntimeError:
                print('Nece da apdejtuje bazu kako treba')
                mydb.rollback()
            else:
                mydb.commit()
            # defender_klijent['squads'] = preostali_squadovi

        dmg_done = battle_info.get('dmgDone')
        post_status = battle_info.get('defenderPostStatus')

        # todo posalji webhook napadnutom
        posaljinapadnutom_attackwebhook(napadninjegatoken, token_napadaca, dmg_done, post_status)

        # todo posalji webhook napadacu (ovo je za moj log)
        posaljinapadacu_attackwebhook(napadninjegatoken, token_napadaca, dmg_done, post_status)

        # battle_info['defenderPostStatus'] = 'Mrtav'
        # # todo izbaci ga iz baze kod mene --------------------------
        if battle_info['defenderPostStatus'] == 'Mrtav':
            try:

                # todo posalji webhooku napadnutom da je MRTAV
                posaljisvima_leavewebhook(napadninjegatoken, mrtav=True)
                obrisi_lika_iz_db_po_tokenu(napadninjegatoken)
                glavna_baza.remove(defender_klijent)
                print('Fja [posaljisvima_joinwebhok]: preostali na bazi')
                pp.pprint(glavna_baza)
            except RuntimeError:
                mydb.rollback()
            else:
                mydb.commit()

        return jsonify(battle_info), 200
    else:
        return error_json('igrac sa tokenom {} (Defender) not found or dead army'.format(napadninjegatoken)), 404


# 2.2 Server API Routes ##### LEAVE #####
#########################################
@app.route('/api/leave', methods=['PUT'])
def api_leave():
    print('Primio API LEAVE')

    # proveravam token
    if request.args.get('accessToken'):
        ucitani_token = request.args.get('accessToken')
        print('=== ZA LEAVE ===')
        print('ekstraktovan token: ', end='')
        print(ucitani_token)
    else:
        print('return 401')
        print()
        return error_json('Ne moze leave komanda bez accessToken-a'), 401

    # TODO FJA-4 Webhook poslati svima info
    posaljisvima_leavewebhook(ucitani_token)
    print('return 202')

    return success_json(
        'Ok brale vidimo se kasnije, to rejoin WITH SAME ARMY use accessToken={} '.format(ucitani_token)
    ), 202


if __name__ == '__main__':
    postavi_bazu()
    app.run(debug=True)
