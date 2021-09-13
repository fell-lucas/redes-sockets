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

class Server:

	def __init__(self):
		self.clients = {}
		self.address = {}
		self.server = None

	def bind(self):
		'''
			DESC: Cria um servidor e relaciona a um IP
			ARGS: self
			RETURN: None
		'''
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			
			self.server.bind((HOST, PORT))
			self.server.listen(CLIENT_LIMIT)
			print(f'Listening on {HOST}:{PORT}')
 
		except socket.error as e:
			print(f'[ERROR] {e}')

	def receive_message(self, client, header):
		'''
			DESC: Recebe mensagem de um cliente
			ARGS: 
				client (socket client): Cliente enviando a mensagem
				header (int): Comprimento da mensagem
			RETURN: msg (str): A mensagem em formato de texto
		'''
		chunk = b''

		while len(chunk) < header:
			packet = client.recv(BUFFER)
			chunk += packet 

		msg = pickle.loads(chunk[:header])
		return msg 

	def send_message(self, username, msg):
		'''
			DESC: Transmite a mensagem para os outros clientes
			ARGS: 
				msg (str): Mensagem a ser enviada 
				username (str): Nome do usuário remetente
			RETURN: None
		'''
		msg = pickle.dumps(f'{username} >> {msg}')
		header = f'{len(msg):0{HEADER}d}'

		for key, client in self.clients.items():
			if key != username:
				 client.send(pickle.dumps(header))
				 time.sleep(0.01)
				 client.send(msg)

	def communicate(self, username):
		'''
			DESC: Se comunica com um cliente específico
			ARGS: 
				username (str): Identificador do cliente
			RETURN: None 
		'''
		client = self.clients[username]

		while True:
			packet = client.recv(BUFFER)
			header = int(pickle.loads(packet))
			msg = self.receive_message(client, header)
			
			if msg == '[quit]':
				break	

			self.send_message(username, msg)

		del self.clients[username]
		
		self.send_message('[SERVER]', f'[{username}] has left the chat')
		print(f'Connection with {self.address[username]} terminated')
		client.close()
	
		del self.address[username]
		sys.exit()


	def connect(self):
		'''
			DESC: Estabelece conexão com diferentes clientes
			ARGS: self
			RETURN: None 
		'''
		while True:
			client, address = self.server.accept()
			print(f'Connection established from {address}')

			username = pickle.loads(client.recv(BUFFER))
			self.send_message('[SERVER]', f'{username} has joined the chat')

			self.clients[username] = client
			self.address[username] = address

			thread = Thread(target=self.communicate, args=(username,), daemon=True)
			thread.start() 

if __name__ == '__main__':
	server = Server()
	server.bind()
	server.connect()