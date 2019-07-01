from sys import exit
from socket import *
from threading import *
import struct

lock = Lock()
def_cod = "utf-8"

class Comunicacao():
    def __init__(self):
        # self._sock_receptor = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        # self._sock_receptor.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        #
        # self._sock_remetente = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        # self._sock_remetente.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 1)
        # self._sock_receptor.setblocking(False) # Tornando o socket com o tipo de chamada não bloqueante

        self._sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, 1)
        self._sock.setblocking(False)  # Tornando o socket com o tipo de chamada não bloqueante

        self.mcast_group = '239.0.0.1'
        self.mcast_port = 6000
        self.mcast_addrss = (self.mcast_group, self.mcast_port)
        self.p_len = 4
        self.LENMAX = 1240
        # self._client_list = []

    def bind(self):
        try:
            self._sock.bind(('', self.mcast_port))

            mreq = struct.pack("4sl", inet_aton(self.mcast_group), INADDR_ANY)

            self._sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
        except Exception as e:
            print(str(e))

    def receber(self):

        # header = None
        msg = None

        # if header is None:
        #     header = self._read_header()

        # if header:
        #     pass
        if msg is None:
            try:
                msg = self._read_msg(1024)
            except BlockingIOError:
                return None

        return msg.decode(def_cod)

    def enviar(self, msg):
        ''' Método para envio de mensagens'''
        data = self._cod_msg(msg)

        total_len = len(data)
        totalsent = 0

        while totalsent < total_len:
            sent = self._sock.sendto(data[totalsent:], self.mcast_addrss)  # min(totalsent + self.LENMAX, total_len - totalsent)
            if sent == 0:
                raise RuntimeError("enviar: Conexão socket quebrada")

            totalsent += sent

    def _read_header(self):
        chunks = []
        bytes_recv = 0
        while bytes_recv < self.p_len:
            chunk = self._sock.recv(min(self.LENMAX, self.p_len - bytes_recv))
            if chunk == b'':
                raise RuntimeError("Read Header: Conexão quebrada")
            chunks.append(chunk)
            bytes_recv = bytes_recv + len(chunk)

        try:
            return int(b''.join(chunks))
        except ValueError:
            raise RuntimeError("Read Header: Recebido valor inesperado !int = {}".format(b''.join(chunks)))

    def _read_msg(self, msg_len):
        chunks = []
        # bytes_recv = 0
        # while bytes_recv < msg_len:
        #     pass
        chunk = self._sock.recv(msg_len)
        if chunk == b'':
            raise RuntimeError("read msg: Conexão Quebrada")
        chunks.append(chunk)
        # bytes_recv = bytes_recv + len(chunk)
        return b''.join(chunks)

    def _cod_msg(self, msg):

        msg_cod = msg.encode(def_cod)
        # hdr_len = str(len(msg_cod))  # tamanho do cabeçalho
        #
        # if len(hdr_len) < self.p_len:
        #     # caso o cabeçalho tenha uma quantidade de algarismos menor do que a esperada, será concatenado a quantidade de zeros necessaria na frente
        #     hdr_len = '0' * (self.p_len - len(hdr_len)) + hdr_len
        # elif len(hdr_len) > self.p_len:
        #     raise RuntimeError("cod msg: Cabeçalho maior que", self.p_len, "bytes") # poderia tratar quebrando a mensagem

        # hdr_len.encode(def_cod) +
        return  msg_cod  # Dado que será efetivamente enviado = (proto cabeçalho + cabeçalho).encode + mensagem codificada
