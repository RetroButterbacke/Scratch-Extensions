import asyncio
import websockets
import aioconsole
import os
import re
import math

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

    print(f'Client connected from {websocket.remote_address}')
    prompt_refreshed = True

    if websocket not in client_sockets:
        await websocket.send(str(nextSessionID))
        login_data = await websocket.recv()
        print(login_data)
        if login_data:
            login_data_list = login_data.split(';')
            if login_data_list[0] == 'create':
                nextSessionID = int(login_data_list[1])
            client_sockets.append(websocket)
            sessionID = login_data_list[2]
            if sessionID not in sessionIDs:
                sessionIDs.append(sessionID)
            if login_data_list[0] == 'create':
                sessions[sessionID] = {'player1': websocket, 'player2': None, 'variables': [], 'varp1': [], 'varp2': [], 'round_end': False}
                session_complete[sessionID] = False
            else:
                if sessionID in sessions:
                    sessions[sessionID]['player2'] = websocket
                    session_complete[sessionID] = True
                    await websocket.send("ss")
                else:
                    await websocket.send("nss")
            users_session[websocket] = sessionID
            user_names[websocket] = login_data_list[3]

    try:
        while True:
            sessionID = users_session[websocket]
            if session_complete[sessionID] is True:
                await checkSessionData(websocket)
            message = await websocket.recv()

            if str(message).startswith("request:"):
                if "full_party" in message:
                    await websocket.send(str(session_complete[sessionID]).lower())
                if session_complete[sessionID]:
                    if "user_names" in message:
                        session = sessions[sessionID]
                        p1_name = user_names[session["player1"]]
                        p2_name = user_names[session["player2"]]
                        send = f"{p1_name};{p2_name}"
                        await websocket.send(send)
                    if "sessionData" in message:
                        session = sessions[sessionID]
                        if session['variables']:
                            sessionData = re.sub(';', ';', ';'.join(session['variables']))
                            await websocket.send(sessionData)
                        else:
                            await websocket.send("null")
                    if "round_end" in message:
                        session = sessions[sessionID]
                        await websocket.send(str(session['round_end']).lower())

            elif str(message).startswith("set:"):
                if "sessionData:" in message:
                    match = re.match(r'^set: sessionData:(.*)$', message)
                    if match:
                        sessionData = match.group(1).strip()
                    session = sessions[sessionID]
                    if session['variables']:
                        if session['player1'] is websocket:
                            session['varp1'] = sessionData.split(";")
                        else:
                            session['varp2'] = sessionData.split(";")
                    elif session['player1'] is websocket:
                        session['variables'] = sessionData.split(";")
                if "round_end" in message:
                    session = sessions[sessionID]
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
        except Exception as ex:
            print(f"Error handling disconnection: {ex}")
        print(f"Removed client {websocket.remote_address}. Active clients: {len(client_sockets)}")
        prompt_refreshed = True

async def stop_server():
    print("Stopping server...")
    close_tasks = [websocket.close() for websocket in client_sockets]
    await asyncio.gather(*close_tasks)

def calcMove(x, y, dir, steps):
    x = float(x)
    y = float(y)
    dir = float(dir)
    steps = float(steps)
    angle = 0
    if dir >= 0:
        angle = 90 - dir
    else:
        angle = dir + 90
    adjacent_side = 0
    if dir < 0:
        adjacent_side = math.cos(math.radians(angle)) * -steps
    else:
        adjacent_side = math.cos(math.radians(angle)) * steps
    opposite_side = math.sin(math.radians(angle)) * steps
    new_x = round((x + adjacent_side), 2)
    new_y = round((y + opposite_side), 2)
    return (new_x, new_y)

async def checkSessionData(websocket):
    # Get user data
    sessionID = users_session[websocket]
    session = sessions[sessionID]
    variables = session['variables']
    varp1 = session['varp1']
    varp2 = session['varp2']
    if not (len(varp1) > 0 and len(varp2) > 0):
        return
    # Check ball dir first
    if varp1[3] != varp2[3]:
        session['variables'] = varp1
        return
    # Check x and y coords
    x, y = calcMove(variables[0], variables[1], variables[2], 10 * float(variables[7]))
    xTo0p1 = float(varp1[0]) - float(x)
    yTo0p1 = float(varp1[1]) - float(y)
    xTo0p2 = float(varp2[0]) - float(x)
    yTo0p2 = float(varp2[1]) - float(y)
    if xTo0p1 < xTo0p2:
        variables[0] = str(varp1[0])
    else:
        variables[0] = str(varp2[0])
    if yTo0p1 < yTo0p2:
        variables[1] = str(varp1[1])
    else:
        variables[1] = str(varp2[1])
    # Check player positions // I know its not the best way but it would be a low chance that both are cheating
    if not float(varp1[3]) > float(variables[3]) + 10 or not float(varp1[3]) < float(variables[3]) - 10:
        variables[3] = str(varp1[3])
    else:
        variables[3] = str(varp2[3])
    if not float(varp2[4]) > float(variables[4]) + 10 or not float(varp2[4]) < float(variables[4]) - 10:
        variables[4] = str(varp2[4])
    else:
        variables[4] = str(varp1[4])
    # Check scores
    if float(varp1[5]) > float(varp2[5]):
        if not float(varp1[5]) > float(variables[5]) + 1 and not float(varp1[5]) < float(variables[5]):
            variables[5] = str(varp1[5])
        else:
            variables[5] = str(varp2[5])
    else:
        if not float(varp2[5]) > float(variables[5]) + 1 and not float(varp2[5]) < float(variables[5]):
            variables[5] = str(varp2[5])
        else:
            variables[5] = str(varp1[5])
    if float(varp1[6]) > float(varp2[6]):
        if not float(varp1[6]) > float(variables[6]) + 1 and not float(varp1[6]) < float(variables[6]):
            variables[6] = str(varp1[6])
        else:
            variables[6] = str(varp2[6])
    else:
        if not float(varp2[6]) > float(variables[6]) + 1 and not float(varp2[6]) < float(variables[6]):
            variables[6] = str(varp2[6])
        else:
            variables[6] = str(varp1[6])
    # Check game speed
    print(varp1[7])
    variables[7] = str(varp1[7])

    print(sessions[users_session[websocket]]['variables'])

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
