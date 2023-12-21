import asyncio
import websockets
import aioconsole
import os
import re
import keyboard

PORT = 4338
nextSessionID = 0
prompt_refreshed = False
sessionIDs = []
client_sockets = []
users_session = {}
sessions = {}
session_complete = {}
user_names = {}

async def handle_connection(websocket, path):
    global nextSessionID
    global sessionIDs
    global client_sockets
    global users_session
    global sessions
    global session_complete
    global user_names
    global prompt_refreshed
    game_speed = 0

    print(f'Client connected from {websocket.remote_address}')
    prompt_refreshed = True

    if not websocket in client_sockets:
        await websocket.send(str(nextSessionID))
        login_data = await websocket.recv()
        print(login_data)
        if login_data:
            login_data_list = login_data.split(';')
            if login_data_list[0] == 'create':
                nextSessionID = int(login_data_list[1])
            client_sockets.append(websocket)
            sessionID = login_data_list[2]
            if not sessionID in sessionIDs:
                sessionIDs.append(sessionID)
            if login_data_list[0] == 'create':
                sessions[sessionID] = {'player1': websocket, 'player2': None, 'variables': [], 'varp1': [], 'varp2': [], 'round_end': False}
                session_complete[sessionID] = False
            else:
                if sessions.__contains__(sessionID):
                    sessions[sessionID]['player2'] = websocket
                    session_complete[sessionID] = True
                    await websocket.send("ss")
                else:
                    await websocket.send("nss")
            users_session[websocket] = sessionID
            user_names[websocket] = login_data_list[3]

    try:
        while True:
            checkSessionData()
            message = await websocket.recv()

            print(message)

            if str(message).startswith("request:"):
                if "full_party" in message:
                    await websocket.send(str(session_complete[users_session[websocket]]).lower())
                if session_complete[users_session[websocket]]:
                    if "user_names" in message:
                        session = sessions[users_session[websocket]]
                        p1_name = user_names[session["player1"]]
                        p2_name = user_names[session["player2"]]
                        send = f"{p1_name};{p2_name}"
                        print(p1_name)
                        print(p2_name)
                        print(send)
                        print(websocket)
                        await websocket.send(send)
                    if "sessionData" in message:
                        session = sessions[users_session[websocket]]
                        if session['variables']:
                            sessionData = re.sub(';', ';', ';'.join(session['variables'])) 
                            await websocket.send(sessionData)
                        else:
                            await websocket.send("null")
                    if "round_end" in message:
                        session = sessions[users_session[websocket]]
                        await websocket.send(str(session['round_end']).lower())

            elif str(message).startswith("set:"):
                if "sessionData:" in message:
                    match = re.match(r'^set: sessionData:(.*)$', message)
                    if match:
                        sessionData = match.group(1).strip()
                    session = sessions[users_session[websocket]]
                    if session['variables']:
                        if session['player1'] is websocket:
                            session['varp1'] = sessionData.split(";")
                            session['varp1'] = [int(x) for x in session['varp1']]
                        else:
                            session['varp2'] = sessionData.split(";")
                            session['varp2'] = [int(x) for x in session['varp2']]
                    elif session['player1'] is websocket:
                        session['variables'] = sessionData.split(";")
                        print(session['variables'])
                if "round_end" in message:
                    session = sessions[users_session[websocket]]
                    session['round_end'] = True
                    
            if prompt_refreshed:
                print(">", end='', flush=True)
                prompt_refreshed = False

            await asyncio.sleep(0)

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client disconnected with code {e.code}, reason: {e.reason}")
        try:
            sessionID = users_session[websocket]
            session = sessions[sessionID]
            session_complete[sessionID] = False
            session['round_end'] = True
            if session['player1'] is websocket:
                session['player1'] = None
                if session['player2'] is None:
                    sessionIDs.remove(sessionID)
                    del sessions[sessionID]
                    del session_complete[sessionID]
                    del user_names[websocket]
                    del users_session[websocket]
                client_sockets.remove(websocket)
            else:
                session['player2'] = None
                if session['player1'] is None:
                    sessionIDs.remove(sessionID)
                    del sessions[sessionID]
                    del session_complete[sessionID]
                    del user_names[websocket]
                    del users_session[websocket]
                client_sockets.remove(websocket)
        except:
            pass
        print(f"Removed client {websocket.remote_address}. Active clients: {len(client_sockets)}")
        prompt_refreshed = True

async def stop_server():
    print("Stopping server...")
    close_tasks = [websocket.close() for websocket in client_sockets]
    await asyncio.gather(*close_tasks)

def calcMove(x, y, dir, steps):
    angle = 0
    if dir >= 0:
        angle = 90 - dir
    else: 
        angle = dir + 90


async def checkSessionData(websocket):
    # Get user data
    session = sessions[users_session[websocket]]
    varp1 = session['varp1']
    varp2 = session['varp2']
    # Check ball dir first
    if not varp1[3] is varp2[3]:
        session['variables'] = varp1
    # Ceck x and y coords
    

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

async def status():
    clear_console()
    print(f"{'Session ID |':<18}{'Active':<15}{'Player 1':<15}{'Player 2':<15}{'Game ended':<15}\n")
    for sessionID in sessionIDs:
        session = sessions[sessionID]
        player1 = ''
        player2 = ''
        if session['player1']:
            player1 = user_names[session['player1']]
        if session['player2']:
            player2 = user_names[session['player2']]
        print(f"{sessionID:<18}{str(session_complete[sessionID]):<15}{player1:<15}{player2:<15}{str(session['round_end']):<15}")

async def main():
    global sessions
    global prompt_refreshed

    start_server = websockets.serve(handle_connection, "127.0.0.1", PORT)

    asyncio.ensure_future(start_server)
    await asyncio.sleep(0)

    print("For commands type help")

    while True:
        command_input = await aioconsole.ainput(">")
        if command_input.lower() == "stop":
            await stop_server()
            break
        elif command_input.lower() == "status":
            await status()
        elif command_input.lower() == "clear":
            clear_console()
        elif command_input.lower() == "help":
            print("Commands:")
            print(" - stop - Stops the server")
            print(" - status - Shows the status of all sessions")
            print(" - clear - Clears the console")
            print(" - help - calls this")
        else:
            print("This command does not exist please type help for help.")

if __name__ == "__main__":
    asyncio.run(main())
