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

SIZE = len(pickle.dumps(f'{0:0{HEADER}d}'))
BUFFER = int(math.pow(2, math.ceil(math.log(SIZE, 2)))) # smallest power of 2 >= SIZE

class Client:

	def __init__(self, username):
		self.client = None 
		self.username = username


	def connect(self):
		'''
			DESC: Conecta ao servidor
			ARGS: self
			RETURN: None
		'''
		try:
			self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.client.connect((HOST, PORT))
			print(f'Connected to {HOST}:{PORT}')
			self.client.send(pickle.dumps(self.username))

			thread = Thread(target=self.communicate, daemon=True)
			thread.start()
			self.send_messages()

		except socket.error as e:
			print(f'[ERROR] {e}')


	def send_messages(self):
		'''
			DESC: Envia mensagens ao servidor
			ARGS: 
				message (str): Mensagem a ser enviada
			RETURN: None
		'''
		while True:
			message = input(f'{self.username} >> ')
			msg = pickle.dumps(message)
			header = f'{len(msg):0{HEADER}d}'

			self.client.send(pickle.dumps(header))
			time.sleep(0.01)
			self.client.send(msg)

			if message == '[quit]':
				break

		print('[SERVER] >> You have left the chat')
		self.client.close()


	def receive_message(self, header):
		'''
			DESC: Recebe mensagens do servidor
			ARGS: 
				client (socket client): Cliente que enviou a mensagem
				header (int): Comprimento da mensagem
			RETURN: msg (str): A mensagem em formato de texto
		'''
		chunk = b''

		while len(chunk) < header:
			packet = self.client.recv(BUFFER)
			chunk += packet 

		msg = pickle.loads(chunk[:header])
		return msg 


	def communicate(self):
		'''
			DESC: Se comunica com o servidor
			ARGS: self
			RETURN: none
		'''
		while True:
			packet = self.client.recv(BUFFER)
			header = int(pickle.loads(packet))

			msg = self.receive_message(header)
			print(f'\n{msg}\n{self.username} >> ', end="")

if __name__ == '__main__':
	username = input('Enter your username: ')
	client = Client(username)
	client.connect()