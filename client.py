import os
import time
import math
import socket
import pickle 
from threading import Thread
from dotenv import load_dotenv

# Constantes
PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(PATH)

HOST = socket.gethostbyname(os.getenv('HOST'))
PORT = int(os.getenv('PORT'))
HEADER = int(os.getenv('HEADER'))

SIZE = len(pickle.dumps(f'{0:0{HEADER}d}')) # '{0:0{HEADER}d}' = "0000"
BUFFER = int(math.pow(2, math.ceil(math.log(SIZE, 2)))) # smallest power of 2 >= SIZE

username = ""

def connect(username):
	try:
		#Criação e conexão do socket
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))
		print(f'Connected to {HOST}:{PORT}')

		#Transforma em bytes e envia para o server
		s.send(pickle.dumps(username))

		thread = Thread(target=communicate, args=(s,), daemon=True)
		thread.start()

		send_messages(s)

	except socket.error as e:
		print(f'[ERROR] {e}')

# Recebe os pacotes vindos do servidor, converte os bytes e printa no chat
def communicate(s):
	while True:
		packet = s.recv(BUFFER)
		header = int(pickle.loads(packet))

		chunk = b'' # Leitura em bytes

		while len(chunk) < header: # "Consome" o header até toda a mensagem ser recebida
			packet = s.recv(BUFFER)
			chunk += packet

		msg = pickle.loads(chunk[:header])

		print(f'\n{msg}\n{username} >> ', end="")

# Aguarda a entrada do usuário
def send_messages(s):
	while True:
		message = input(f'{username} >> ')
		msg = pickle.dumps(message)

		#Define o tamanho do header
		header = f'{len(msg):0{HEADER}d}'

		#Codificação e envio da mensagem
		s.send(pickle.dumps(header))
		time.sleep(0.01)
		s.send(msg)
		
		if message == '/quit':
			break

	print('[SERVER] >> You have left the chat')
	s.close()

if __name__ == '__main__':
	username = input('Enter your username: ')
	connect(username)