from socket import socket, gethostname, gethostbyname, AF_INET, SOCK_STREAM

# O servidor a seguir foi escrito com base no seu funcionamento no localhost,
# por isso, todos os usuários que se conectam a ele terao o mesmo IP.
# Isso nos fez optar pelo uso de diferentes portas para identificar os usuarios
# do cliente, que sao definidas ao abrir a aplicacao.
# Outro motivo o uso de diferentes portas para os clientes vem do fato de que
# duas instancias no localhost nao conseguem ouvir a mesma porta simultaneamente
# para esperar por mensagens, o que novamente nos leva ao uso de diferentes
# portas para cada usuario

HOST = ''
PORT = 10000 # porta para servidor

listener = socket(AF_INET, SOCK_STREAM)
origem = (HOST, PORT)
listener.bind(origem)

listener.listen(1) # listener espera mensagens dos usuarios

usuarios = []

print("Aguardando abertura do cliente")

while True:
    con, cliente = listener.accept() # aceita transacao tcp

    porta_cliente, msg = con.recv(1024).decode().split('|') # recebe conteudo do pacote, divide entre porta do usuario que o identifica e mensagem da camada de aplicacao
    porta_cliente = int(porta_cliente)

    if not msg: break

    con.close()

    _, usr, ctrl = msg.split('/') # extrai dados da mensagem

    if usr == 'CN_SIGN' and ctrl == '\x18': # se mensagem for comando de conexao
        try:
            usuarios.index(porta_cliente) # verifica se usuario ja esta conectado
        except: # caso contrario
            usuarios.append(porta_cliente) # adiciona usuario a lista de clientes
            print(f'Novo usuário {porta_cliente} adicionado.')
    elif usr == 'DC_SIGN' and ctrl == '\x18': # se mensagem for comando de desconexao
        try:
            usuarios.remove(porta_cliente)  # remove usuario da lista de clientes
            print(f'Usuário {porta_cliente} desconectado do servidor.')
        except:
            print('ERRO: Usuário não encontrado.')
    else: # se mensagem for algo enviado para o chat
        for user in usuarios: # repassa mensagem para todos os usuarios conectados por transacao tcp
            hostname = gethostname()
            host = gethostbyname(hostname)

            output = socket(AF_INET, SOCK_STREAM)
            destino = (host, user)

            output.connect(destino)

            output.send(msg.encode())

    
