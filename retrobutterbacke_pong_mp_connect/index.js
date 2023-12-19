const BlockType = require('../../extension-support/block-type');
const ArgumentType = require('../../extension-support/argument-type');
const TargetType = require('../../extension-support/target-type');


class Socket {
    constructor(ipAddress, port) {
        this.websocket = new WebSocket("ws://" + ipAddress + ":" + port);
        this.connectionEstablished = false;
        this.receivedData = '';
        this.errorOccured = false;

        this.initPromise = new Promise((resolve, reject) => {
            this.websocket.addEventListener('readystatechange', () => {
                if (this.websocket.readyState === WebSocket.CLOSED) {
                    console.error('WebSocket connection failed or closed.');
                    this.connectionEstablished = false;
                }
            });

            this.websocket.addEventListener('open', (event) => {
                console.log('WebSocket connection opened:', event);
                this.connectionEstablished = true;
                this.recievedData = '';
                resolve();
            });

            this.websocket.addEventListener('close', (event) => {
                console.log('WebSocket connection closed:', event);
                this.connectionEstablished = false;
            });

            this.websocket.addEventListener('error', (event) => {
                console.error('WebSocket error:', event);
                this.errorOccured = true;
                reject(event);
            });
        });
    }

    async init() {
        await this.initPromise; // Wait for the connection to be established

        return new Promise((resolve, reject) => {
            const messageHandler = (event) => {
                this.receivedData = event.data;
                this.websocket.removeEventListener('message', messageHandler);
                resolve();
            };

            if (this.connectionEstablished) {
                this.websocket.addEventListener('message', messageHandler);
            } else {
                reject(new Error('WebSocket connection not established.'));
            }
        });
    }

    async clearReceivedData() {
        while (true) {
            let data = await this.receiveData();
            if (data.length === 0) {
                break;
            }
        }
    }

    async receiveData() {
        return new Promise((resolve) => {
            if (this.receivedData !== '') {
                resolve(this.receivedData);
                this.receivedData = '';
            } else {
                const dataHandler = (event) => {
                    this.receivedData = event.data;
                    this.websocket.removeEventListener('message', dataHandler);
                    resolve(this.receivedData);
                };

                this.websocket.addEventListener('message', dataHandler);
            }
        });
    }

    async send(message) {
        return new Promise((resolve, reject) => {
            if (this.connectionEstablished) {
                this.websocket.send(message);
                resolve();
            } else {
                reject(new Error('WebSocket connection not open. Unable to send message:', message));
            }
        });
    }

    closeConnection() {
        this.websocket.close();
    }

    getConnection() {
        return this.connectionEstablished;
    }

    checkErrors() {
        return this.errorOccured;
    }
}



class Scratch3PongMPConnect {
    constructor (runtime) {
        this.runtime = runtime;
        this.nextSessionID = 0;
        this.sessionID = -1;
        this.full_party = false;
        this.round_end = false;
        this.posx = 9;
        this.posy = 4;
        this.sessionData = "";
    }

    _buildMenu (info) {
        return info.map((entry, index) => {
            const obj = {};
            obj.text = entry.name;
            obj.value = String(index + 1);
            return obj;
        });
    }

    get REQUEST_ITEMS () {
        return [
            {
                name: 'session variables'
            },
            {
                name: 'names'
            },
            {
                name: 'full party'
            },
            {
                name: 'has round ended'
            },
            {
                name: 'round end'
            }
        ]
    }

    get CONNECTION_TYPES () {
        return [
            {
                name: 'Create'
            },
            {
                name: 'Connect'
            }
        ]
    }

    getInfo() {
        return {
            id: 'pongMPConnect',
            name: 'Pong Multiplayer Connect',
            color1: '#13562C',
            color2: '#0F8E3E',
            blocks: [
                {
                    opcode: 'init',
                    blockType: BlockType.COMMAND,
                    text: 'init [ipAddress] [port] [user_name] [connection_type] [session_id]',
                    arguments: {
                        ipAddress: {
                            defaultValue: '127.0.0.1',
                            type: ArgumentType.STRING
                        },
                        port: {
                            defaultValue: 4338,
                            type: ArgumentType.NUMBER
                        },
                        user_name: {
                            defaultValue: 'dummy',
                            type: ArgumentType.STRING
                        }, 
                        connection_type: {
                            type: ArgumentType.NUMBER,
                            menu: 'CONNECTION_TYPE',
                            defaultValue: 1
                        },
                        session_id: {
                            type: ArgumentType.NUMBER,
                            defaultValue: 0
                        }
                    }
                },
                {
                    opcode: 'updateSessionVariabls',
                    blockType: BlockType.COMMAND,
                    text: 'update session variables [ball_x],[ball_y],[ball_rotation],[p1_y],[p2_y],[p1_points],[p2_points],[game_speed]',
                    arguments: {
                        ball_x: {
                            defaultValue: 9,
                            type: ArgumentType.NUMBER
                        },
                        ball_y: {
                            defaultValue: 4,
                            type: ArgumentType.NUMBER
                        },
                        ball_rotation: {
                            defaultValue: 0,
                            type: ArgumentType.NUMBER
                        },
                        p1_y: {
                            defaultValue: 26,
                            type: ArgumentType.NUMBER
                        },
                        p2_y: {
                            defaultValue: 26,
                            type: ArgumentType.NUMBER
                        },
                        p1_points: {
                            defaultValue: 0,
                            type: ArgumentType.NUMBER
                        },
                        p2_points: {
                            defaultValue: 0,
                            type: ArgumentType.NUMBER
                        },
                        game_speed: {
                            defaultValue: 0.75,
                            type: ArgumentType.NUMBER
                        }
                    }
                },
                {
                    opcode: 'calcMove',
                    blockType: BlockType.COMMAND,
                    text: 'calculate new coordinates [posx] [posy] [dir] [steps]',
                    arguments: {
                        posx: {
                            type: ArgumentType.NUMBER,
                            defaultValue: 9
                        },
                        posy: {
                            type: ArgumentType.NUMBER,
                            defaultValue: 4
                        },
                        dir: {
                            type: ArgumentType.NUMBER,
                            defaultValue: 0
                        },
                        steps: {
                            type: ArgumentType.NUMBER,
                            defaultValue: 0
                        }
                    }
                },
                {
                    opcode: 'request',
                    blockType: BlockType.COMMAND,
                    text: 'request [message]',
                    arguments: {
                        message: {
                            type: ArgumentType.NUMBER,
                            menu: 'REQUEST',
                            defaultValue: 1
                        }
                    }
                },
                {
                    opcode: 'log',
                    blockType: BlockType.COMMAND,
                    text: 'print [message]',
                    arguments: {
                        message: {
                            type: ArgumentType.STRING,
                            defaultValue: 'ok'
                        }
                    }
                },
                {
                    opcode: 'resetPlayerNames',
                    blockType: BlockType.COMMAND,
                    text: 'reset player names'
                },
                {
                    opcode: 'closeConnection',
                    blockType: BlockType.COMMAND,
                    text: 'close connection',
                },
                {
                    opcode: 'getSessionID',
                    blockType: BlockType.REPORTER,
                    text: 'session id'
                },
                {
                    opcode: 'receive',
                    blockType: BlockType.REPORTER,
                    text: 'receive',
                },
                {
                    opcode: 'ballx',
                    blockType: BlockType.REPORTER,
                    text: 'ball_x',
                },
                {
                    opcode: 'bally',
                    blockType: BlockType.REPORTER,
                    text: 'ball_y',
                },
                {
                    opcode: 'ballrotation',
                    blockType: BlockType.REPORTER,
                    text: 'ball_rotation',
                },
                {
                    opcode: 'p1y',
                    blockType: BlockType.REPORTER,
                    text: 'p1_y',
                },
                {
                    opcode: 'p2y',
                    blockType: BlockType.REPORTER,
                    text: 'p2_y',
                },
                {
                    opcode: 'p1points',
                    blockType: BlockType.REPORTER,
                    text: 'p1_points',
                },
                {
                    opcode: 'p2points',
                    blockType: BlockType.REPORTER,
                    text: 'p2_points',
                },
                {
                    opcode: 'gamespeed',
                    blockType: BlockType.REPORTER,
                    text: 'game_speed',
                },
                {
                    opcode: 'p1',
                    blockType: BlockType.REPORTER,
                    text: 'Player 1',
                },
                {
                    opcode: 'p2',
                    blockType: BlockType.REPORTER,
                    text: 'Player 2',
                },
                {
                    opcode: 'calc_posx',
                    blockType: BlockType.REPORTER,
                    text: 'calculatet pos x',
                },
                {
                    opcode: 'calc_posy',
                    blockType: BlockType.REPORTER,
                    text: 'calculatet pos y',
                },
                {
                    opcode: 'fp',
                    blockType: BlockType.BOOLEAN,
                    text: 'check full party'
                },
                {
                    opcode: 'nss',
                    blockType: BlockType.BOOLEAN,
                    text: 'no such session'
                },
                {
                    opcode: 'roundEnd',
                    blockType: BlockType.BOOLEAN,
                    text: 'end of round'
                },
                {
                    opcode: 'getConnection',
                    blockType: BlockType.BOOLEAN,
                    text: 'connection established',
                },
                {
                    opcode: 'checkErrors',
                    blockType: BlockType.BOOLEAN,
                    text: 'check for errors'
                }
            ],
            menus: {
                REQUEST: {
                    acceptReporters: true,
                    items: this._buildMenu(this.REQUEST_ITEMS)
                },
                CONNECTION_TYPE: {
                    acceptReporters: true,
                    items: this._buildMenu(this.CONNECTION_TYPES)
                }
            }
        };
    }

    async init({ ipAddress, port, user_name, connection_type, session_id }) {
        try {
            if (connection_type == 2) this.sessionID = session_id 
            if (this.socket != null && this.socket.getConnection()) this.socket.closeConnection();
            this.socket = new Socket(ipAddress, port);
            await this.socket.init();
            if (this.socket.getConnection()) {
                this.nextSessionID = parseInt(await this.socket.receiveData());
                if (this.sessionID == -1) {
                    this.sessionID = this.nextSessionID;
                    this.nextSessionID += 1;
                }
                let login_data = ''
                if (connection_type == 1)
                    login_data = `create;${this.nextSessionID};${this.sessionID};${user_name}`;
                else
                    login_data = `connect;${this.nextSessionID};${this.sessionID};${user_name}`;
                await this.socket.send(login_data);
                if (connection_type == 2)
                    if (await this.socket.receiveData() == "nss") this.noSuchSession = true; else this.noSuchSession = fasle;
            }
        } catch (error) {
            console.error('Error during socket initialization:', error);
        }
    }
    

    async updateSessionVariabls ({ ball_x, ball_y, ball_rotation, p1_y, p2_y, p1_points, p2_points, game_speed }) {
        if (this.socket.getConnection()) {
            this.sessionData = "set: sessionData:" + ball_x + ";" + ball_y + ";" + ball_rotation + ";" + p1_y + ";" + p2_y + ";" + p1_points + ";" + p2_points + ";" + game_speed;
            await this.socket.send(this.sessionData);
        }
    }

    calcMove ({posx, posy, dir, steps}) {
        let angle = 0;
        if (dir >= 0) angle = 90 - dir;
        else angle = dir + 90;
        // Convert to radians
        angle = (angle * Math.PI) / 180;
        let adjacent_side = Math.cos(angle) * steps;
        let opposite_side = Math.sin(angle) * steps;
        this.posx = Math.round((posx + adjacent_side) * 100) / 100;
        this.posy = Math.round((posy + opposite_side) * 100) / 100;
    }

    log ({ message }) {
        console.log(message);
    }

    resetPlayerNames () {
        this.player1 = '';
        this.player2 = '';
    }

    nss () {
        result = this.noSuchSession;
        this.noSuchSession = false;
        return this.result;
    }

    roundEnd () {
        return this.round_end;
    }

    async request ({ message }) {
        if ((this.socket != null) && this.socket.getConnection())
            //clear the recieve...
            this.socket.clearReceivedData();
            //send the new message to the server...
            if (message == 1) {
                await this.socket.send("request: sessionData");
                let response = await this.socket.receiveData();
                let data = response.split(";");
                this.ball_x = data[0];
                this.ball_y = data[1];
                this.ball_rotation = data[2];
                this.p1_y = data[3];
                this.p2_y = data[4];
                this.p1_points = data[5];
                this.p2_points = data[6];
                this.game_speed = data[7];
            } else if (message == 2) {
                await this.socket.send("request: user_names");
                let response = await this.socket.receiveData();
                console.log(response);
                let names = response.split(";");
                this.player1 = names[0];
                this.player2 = names[1];
            } else if (message == 3)  {
                await this.socket.send("request: full_party");
                let response = await this.socket.receiveData();
                console.log(response);
                if (response == 'true') this.full_party = true; else this.full_party = false;
            } else if (message == 4) {
                await this.socket.send("request: round_end");
                let response = await this.socket.receiveData();
                if (response == 'true') this.round_end = true; else this.round_end = false;
            } else if (message == 5) {
                await this.socket.send("set: round_end");
            }
    }

    receive () {
        if ((this.socket != null) && this.socket.getConnection())
            return this.socket.receiveData();
        return '';
    }

    getConnection () {
        if ((this.socket != null) && this.socket.getConnection())
            return this.socket.getConnection();
    }

    fp () {
        return this.full_party;
    }

    checkErrors () {
        return this.socket.checkErrors();
    }

    closeConnection () {
        this.sessionID = -1;
        this.full_party = false;
        this.round_end = false;
        if ((this.socket != null) && this.socket.getConnection())
            this.socket.closeConnection();
    }

    getSessionID () {
        return this.sessionID;
    }

    ballx () {
        return this.ball_x;
    }
    
    bally () {
        return this.ball_y;
    }

    ballrotation () {
        return this.ball_rotation;
    }

    p1y () {
        return this.p1_y;       
    }

    p2y () {
        return this.p2_y;
    }

    p1points () {
        return this.p1_points;
    }

    p2points () {
        return this.p2_points;
    }

    gamespeed () {
        return this.game_speed;
    }

    p1 () {
        return this.player1;
    }

    p2 () {
        return this.player2;
    }

    calc_posx () {
        return this.posx;
    }
    
    calc_posy () {
        return this.posy;
    }

}

module.exports = Scratch3PongMPConnect;