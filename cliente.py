import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import WIN_CLOSED

import sys
from threading import Thread
from time import localtime

SERVER_PORT = 10000
user_port = 0

def chat_listener(): # funcao espera mensagens enviadas no chat
    from socket import socket, AF_INET, SOCK_STREAM

    connect() # se conecta ao servidor

    tcp_listener = socket(AF_INET, SOCK_STREAM)
    origem = ('', user_port)
    tcp_listener.bind(origem)

    tcp_listener.listen(1) # comeca a ouvir porta do usuario

    print('Ouvindo agora a porta', user_port)

    while True:
        con, _ = tcp_listener.accept()

        time, username, msg = con.recv(1024).decode().split('/') # capta mensagem
        if not msg: break
        new_message(time, username, msg) # e a envia para o chat

        con.close()

    tcp_listener.close()

def send_message(msg): # envia mensagem para o servidor
    from socket import socket, gethostname, gethostbyname, AF_INET, SOCK_STREAM

    hostname = gethostname()
    host = gethostbyname(hostname)

    tcp = socket(AF_INET, SOCK_STREAM)
    destino = (host, SERVER_PORT)

    time = localtime() # capta horario do usuario

    horas = f'{time.tm_hour:02d}'
    minutos = f'{time.tm_min:02d}'

    msg = f'{user_port}|{horas}:{minutos}/{msg}' # monta mensagem no formato [porta do usuario]|[horario]/[nome de usuario]/[mensagem]

    tcp.connect(destino)

    tcp.send(msg.encode()) # envia mensagem

    tcp.close()

def new_message(time, usr, msg):
    window['_chat_'].print(f'{time} - {usr}: {msg}\n') # adiciona mensagem a interface grafica do cliente

def connect():
    send_message('CN_SIGN/\x18') # envia comando de conexao

def disconnect():
    send_message('DC_SIGN/\x18') # envia comando de desconexao

# --------------------------- Layout da interface grafica -------------------------------------

sg.theme('LightGrey')
frame_layout = [
    [sg.Multiline(key='_chat_', disabled=True, size=(100, 30))]
]

sg.theme('LightGrey')
layout = [
    [sg.T('Trabalho realizado pelos acadêmicos: André e Eduardo')],
    [sg.T('Nome de usuário: '), sg.I(key='_username_', size=30)],
    [sg.Multiline(key='_input_', size=(100)), sg.B('Enviar', key='_send_')],
    [sg.HorizontalSeparator()],
    [
        sg.Frame(
            title='Chat: ',
            layout=frame_layout,
            size=(400 * 2, 400),
            pad=(0, 0),
            key='_chat_window_'
        )
    ]
]

window = sg.Window('Zipper-Zopper', layout)

# ---------------------------------------------------------------------------------------------

def main():
    global user_port
    user_port = int(sys.argv[1]) # grava porta definida na compilacao

    listener = Thread(target=chat_listener) # cria thread para 'ouvir' o chat
    listener.daemon = True # flag garante que thread sera terminada junto com o cliente
    listener.start() # inicia a thread

    while True: # mantem a janela grafica
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Sair'): # ao sair
            disconnect() # desconecta o usuario
            break # escapa do loop
        elif event == '_send_': # ao enviar mensagem
            msg = values['_username_'] + '/' + values['_input_'] # capta mensagem
            window['_input_'].update('') # limpa caixa de mensagem
            send_message(msg) # envia ao servidor

    window.close()

if __name__ == '__main__':
    main()
