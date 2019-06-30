import relogio
import com
import os
import time

comunicacao = com.Comunicacao()
PID = int(os.getpid())


class Sistema:
    def __init__(self):
        self.timeout = 0
        self.ultima_msg = None
        self.alg = None

    def iniciar_bully(self):
        msg = "eleicao"

        comunicacao.enviar(str(PID) + '/' + msg)

        self.alg = BullyInit()

    def iniciar_berkley(self):
        self.alg.iniciar_mudanca()

    def responder(self, resp):
        id = int(resp[:resp.index('/')])
        resp = resp[resp.index('/') + 1:]

        if resp == '/' and id == PID:
            self.timeout += 1

        estado, msg = self.alg.identificar_resposta(id, resp)

        if msg is not None:
            self.ultima_msg = msg

        if estado is not None:
            self.alg = estado

        return msg


class BullySub:
    def identificar_resposta(self, id, resp):
        msg = None
        estado = None

        if PID != id:
            if resp == "berkley":
                msg = "prosseguir"
                estado = BerkleySub()

            elif resp == "eleicao":
                if PID < id:
                    msg = "OK"

        return estado, msg


class BullyInit:

    def identificar_resposta(self, id, resp):
        msg = None
        estado = None

        if PID != id:
            if resp == "OK":
                msg = "berkley"
                estado = BullyLider()

            elif resp == "eleicao":
                if PID > id:
                    msg = "eleicao"
                else:
                    msg = "OK"
                    estado = BullySub()

        return estado, msg


class BullyLider:
    def identificar_resposta(self, id, resp):
        msg = None
        estado = None

        if PID != id:
            if resp == "prosseguir":
                estado = BerkleyLider()

            if resp == "eleicao":
                if PID > id:
                    msg = "eleicao"
                    estado = BullyInit()
                else:
                    msg = "OK"
                    estado = BullySub()

        return estado, msg


class BerkleySub:
    def iniciar_mudanca(self):
        pass

    def identificar_resposta(self, id, resp):
        msg = None
        estado = None
        print("Cheguei Sub")
        return estado, msg

class BerkleyLider:
    def iniciar_mudanca(self):
        pass

    def identificar_resposta(self, id, resp):
        msg = None
        estado = None
        print("Cheguei Lid")
        return estado, msg

def main():

    print("Eu sou", PID)

    comunicacao.bind()

    executor = Sistema()

    executor.iniciar_bully()
    on = True

    while on:

        resp = comunicacao.receber()

        if int(resp[:resp.index('/')]) != PID and resp[resp.index('/')+1:] != '/':
            print("recebido:", resp)

        msg = executor.responder(resp)

        if executor.timeout >= 10:
            print("Deu timeout")
            executor.timeout = 0

        if msg:
            comunicacao.enviar(str(PID) + '/' + msg)
            print("enviado:", str(PID) + '/' + msg)

        else:
            comunicacao.enviar(str(PID) + '//')

        time.sleep(1)


main()