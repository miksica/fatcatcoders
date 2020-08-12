# SERVER & CLIENT APP - Battle simulator
python, flask, api, json, webhooks

1) Prvo pokrenuti oba servera, pa onda slati komande iz event_handler.py.<br/>
2) u njemu su vec zadate komande u loop funkcijama u if __name__ == '__main__' delu<br/>
3) po zelji slati join /attack/ ili leave<br/>  #ove komande su vec definisane kroz funkcije, potrebno je samo RUN-ovati event_handler.py
4) broj klijenata je jednak boju ljudi u listi rndnms posto ih uzima unikatno (trenutno 10 razlicitih imena, #[233] linija koda)
ako se ukloni [rndnms.remove(ime)] sa [68] linije onda moze vise imena ali imena nece biti unikatna<br/><br/>

pozz<br/><br/><br/>

Online battle simulator (FLASK API & JSON).<br/>
Cosists of server and client app<br/>
Server holds all truths, and logs data in DB (MySQL)<br/>
Clients communicate with server via webhooks<br/>
Unlimited number of clients can connect to server, each with unique token<br/>
Each client has his name (Only token has to be unique), number of armies and his unique webhook adress<br/>
For clients to fight, there needs to be minimum of two of them conneceted to server, and have minimum of 1 army<br/>
When client joins on server all other clients get notification of new player joining with their info (name, number of units, webhook)<br/>
Clients can choose to attack strongest, weakest or any random random player<br/>
When client attacks, he need to get a respons from server before he can issue another attack (if he survives)<br/>
<br/>
Attacking rules<br/>
Players attack in their turn untill they hit or untill all hits miss<br/>
Number of attacks untill one is successful is defined by number of units<br/>
Players hit chance is also based on number of units<br/>
Damage is calculated based on number of units in army and the turn on when they hit (...if they hit, the more they miss the less dmg they do)<br/>
Every unit deals 1dmg and has 1hp, but you can take half damage if gods love you. Unit with half hp survives and heals in the next turn<br/>
The less units in army the more chances to take half dmg from an attack<br/>
Reset time, for next attack is calculated by server. The more units in army the longer wait. Server sends status 200 when cooldown is done so client can issue another command<br/>
When clients reaches 0 units he is toasted<br/>
The server is a source of all truths. <br/>
All actions are happening asynchronously. There are no blocking events.<br/>
<br/><br/>
Server API Routes<br/>
<br/>
POST {serverURL}/api/join (optional ?accessToken={accessToken}) -  API route to register client/army<br/>
<br/>
PUT {serverURL}/api/attack/{armyId}?accessToken={accessToken} -  API post to attack an army / 200 for a successful response and 404 for not found or dead army.<br/>
<br/>
PUT {serverURL}/api/leave?accessToken={accessToken} -  API route to leave the battle. To join back, and not register a new army, use join with the accessToken<br/>
<br/>
Server Webhooks (List of webhooks)<br/>
<br/>
army.join - Sent when an army joins the battle. This event is sent to all alive and registered clients.<br/>
Data<br/>
-armyId (id of the joined army)<br/>
-squadsCount (number of squads army have)<br/>
-Type of join (new or returned)<br/>
<br/>
army.leave - Sent when an army activates stop function, leave the game or die. This event is sent to all alive and registered clients.<br/>
Data<br/>
-armyId<br/>
-Type of leave<br/>
<br/>
army.update / Sent every time an army is updated by being attacked or by successfully attacking.<br/>
Data<br/>
-armyId id of the army who was attacked or completed a successful attacking.<br/>
-squadsCount<br/>
-rankRate<br/>
<br/>


