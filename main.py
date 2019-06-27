import relogio
import com
import os

comunicacao = com.Comunicacao()
PID = int(os.getpid())

class Sistema:
    def iniciar_bully(self):
        msg = "eleicao"

        comunicacao.enviar(str(PID) + '/' + msg)

        self.alg = BullyInit()

    def iniciar_berkley(self):
        self.alg.iniciar_mudanca()

    def responder(self, resp):
        id = int(resp[:resp.index('/')])
        resp = resp[resp.index('/') + 1:]

        estado, msg = self.alg.identificar_resposta(id, resp)

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

        if PID != id:
            if resp == "eleicao":
                if PID > id:
                    msg = "eleicao"
                else:
                    msg = "OK"
                mudanca = True

        return mudanca, msg


class BerkleyLider:
    def iniciar_mudanca(self):
        pass

    def identificar_resposta(self, id, resp):
        mudanca = None
        msg = None

        if PID != id:

            if resp == "eleicao":
                if PID > id:
                    msg = "eleicao"
                else:
                    msg = "OK"
                mudanca = True

        return mudanca, msg

def main():

    print("Eu sou", PID)

    comunicacao.bind()

    executor = Sistema()

    executor.iniciar_bully()
    on = True

    while on:

        resp = comunicacao.receber()

        if int(resp[:resp.index('/')]) != PID:
            print("recebido:", resp)

        msg = executor.responder(resp)

        if msg:
            comunicacao.enviar(str(PID) + '/' + msg)
            print("enviado:", str(PID) + '/' + msg)


main()