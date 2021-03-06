import sys
import os
import time
import math
import socket
import pickle # serialização de dados
from threading import Thread
from dotenv import load_dotenv

# Constantes
PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(PATH)

HOST = socket.gethostbyname(os.getenv('HOST'))
PORT = int(os.getenv('PORT'))
HEADER = int(os.getenv('HEADER'))
CLIENT_LIMIT = int(os.getenv('CLIENT_LIMIT'))

SIZE = len(pickle.dumps(f'{0:0{HEADER}d}'))
BUFFER = int(math.pow(2, math.ceil(math.log(SIZE, 2)))) # smallest power of 2 >= SIZE

clientList = {}
addressList = {}

def send_message(username, msg):
	msg = pickle.dumps(f'{username} >> {msg}') # Converte a mensagem para bytes
	header = f'{len(msg):0{HEADER}d}' # Header com o tamanho da mensagem

	for key, client in clientList.items():
		if key != username:
			client.send(pickle.dumps(header))
			time.sleep(0.01)
			client.send(msg)

def receive_message(client, header):
	chunk = b''

	while len(chunk) < header: # "Consome" o header até toda a mensagem ser recebida
		packet = client.recv(BUFFER)
		chunk += packet 

	msg = pickle.loads(chunk[:header])
	return msg 

# Lógica central para recebimento e retransmissão de novas mensagens
def communicate(username):
	client = clientList[username]

	while True:
		packet = client.recv(BUFFER)
		header = int(pickle.loads(packet))
		msg = receive_message(client, header)
		
		if msg == '/quit':
			break	
		
		print(f'{username} spoke: {msg}')
		send_message(username, msg)

	del clientList[username]
	
	send_message('[SERVER]', f'[{username}] has left the chat')
	print(f'Connection with {addressList[username]} terminated')
	client.close()

	del addressList[username]
	sys.exit()

if __name__ == '__main__':
	# Criação do socket
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		
		s.bind((HOST, PORT))
		s.listen(CLIENT_LIMIT)
		print(f'Listening on {HOST}:{PORT}')
 
	except socket.error as e:
		print(f'[ERROR] {e}')

	# Estabelece a conexão de novos clientes
	while True:
		client, address = s.accept()
		print(f'Connection established from {address}')

		username = pickle.loads(client.recv(BUFFER))
		send_message('[SERVER]', f'{username} has joined the chat')

		clientList[username] = client
		addressList[username] = address

		thread = Thread(target=communicate, args=(username,), daemon=True)
		thread.start()