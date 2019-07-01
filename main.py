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
        relogio.iniciar_relogio()

    def iniciar_bully(self):
        msg = "eleicao"

        comunicacao.enviar(str(PID) + '/' + msg)

        self.alg = BullyInit()

    def responder(self, resp):
        if resp is None and self.timeout < 15:
            self.timeout += 1
            id = None
        elif self.timeout >= 15:
            self.timeout = 0
            return "eleicao"
        else:
            id = int(resp[:resp.index('/')])
            resp = resp[resp.index('/') + 1:]

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

        if resp is None:
            return estado, msg

        elif PID != id:
            if resp == "lider":
                msg = "prosseguir"

            elif resp == "berkley":
                estado = BerkleySub()

            elif resp == "eleicao":
                if PID < id:
                    msg = "OK"

        return estado, msg


class BullyInit:

    def identificar_resposta(self, id, resp):
        msg = None
        estado = None

        if resp is None:
            return estado, msg

        elif PID != id:
            if resp == "OK":
                msg = "lider"
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

        if resp is None:
            return estado, msg

        elif PID != id:
            if resp == "prosseguir":
                estado = BerkleyLider()
                msg = "berkley"

            if resp == "eleicao":
                if PID > id:
                    msg = "eleicao"
                    estado = BullyInit()
                else:
                    msg = "OK"
                    estado = BullySub()

        return estado, msg


class BerkleySub:

    @staticmethod
    def identificar_resposta(id, resp):
        msg = None
        estado = None

        if resp is None:
            return estado, msg

        elif resp[0] == '1':
            try:
                tempo = int(resp[resp.index('-') + 1:])
            except ValueError:
                pass
                # raise RuntimeError("berkleysub: Recebido valor inesperado !int = {}".format(resp[resp.index('-') + 1:]))
            else:
                msg = "0-" + str(relogio.get_tempo() - tempo)
                estado = BerkleySub2()

        if PID != id:

            if resp == "eleicao":
                if PID > id:
                    msg = "eleicao"
                    estado = BullyInit()
                else:
                    msg = "OK"
                    estado = BullySub()

        return estado, msg


class BerkleySub2:

    def identificar_resposta(self, id, resp):
        msg = None
        estado = None

        if resp is None:
            return estado, msg

        elif resp[0] == '1':
            try:
                resp = resp[resp.index('-') + 1:]
                tempo = int(resp[:resp.index('/')])
                o_id = int(resp[resp.index('/') + 1:])

            except ValueError:
                raise RuntimeError("berkleysub: Recebido valor inesperado !int = {}".format(resp[resp.index('-') + 1:]))

            if PID == o_id:
                relogio.corrigir_tempo(tempo)
                print("TEMPO CORRIGIDO:", relogio.get_tempo())
                # msg = "final"
                estado = BerkleySub()

        elif PID != id:

            if resp == "eleicao":
                if PID > id:
                    msg = "eleicao"
                    estado = BullyInit()
                else:
                    msg = "OK"
                    estado = BullySub()

        return estado, msg


class BerkleyLider:

    @staticmethod
    def identificar_resposta(id, resp):
        msg = None
        estado = None

        if resp is None:
            t = relogio.get_tempo()
            msg = "1-" + str(t)
            estado = BerkleyLider2(t)

        elif PID != id:
            if resp == "eleicao":
                if PID > id:
                    msg = "eleicao"
                    estado = BullyInit()
                else:
                    msg = "OK"
                    estado = BullySub()

        return estado, msg


class BerkleyLider2:
    def __init__(self, tempo):
        self.tempos = {}
        self.t = tempo

    def identificar_resposta(self, id, resp):
        msg = None
        estado = None

        if resp is None:
            if len(self.tempos) > 1:
                estado = BerkleyLider3(int(sum(self.tempos.values()) / len(self.tempos)), self.tempos)
            else:
                estado = BullyInit()

        elif resp[0] == '1' or resp[0] == '0':
            try:
                tempo = int(resp[resp.index('-') + 1:])
            except ValueError:
                raise RuntimeError("berkleysub: Recebido valor inesperado !int = {}".format(resp[resp.index('-') + 1:]))

            if resp[0] == '1':
                msg = "0-" + str(relogio.get_tempo() - tempo)
            elif resp[0] == '0':
                self.tempos[id] = tempo - int((relogio.get_tempo() - self.t)/2)

        elif PID != id:
            if resp == "eleicao":
                if PID > id:
                    msg = "eleicao"
                    estado = BullyInit()
                else:
                    msg = "OK"
                    estado = BullySub()

        return estado, msg


class BerkleyLider3:
    def __init__(self, tempo, tempos):
        self.tempos = tempos
        self.t = tempo
        self.fechar = False

    def identificar_resposta(self, id, resp):
        msg = None
        estado = None

        if resp is None:
            if not self.fechar:
                try:
                    o_id, tempo = self.tempos.popitem()
                except KeyError:
                    self.fechar = True
                else:
                    msg = "1-" + str(self.t - tempo) + '/' + str(o_id)
            else:
                # msg = "final"
                estado = BerkleyLider()

        elif resp[0] == '1':
            try:
                resp = resp[resp.index('-') + 1:]
                tempo = int(resp[:resp.index('/')])
                o_id = int(resp[resp.index('/') + 1:])

            except ValueError:
                raise RuntimeError("berkleylider3: Recebido valor inesperado !int = {}".format(resp[resp.index('-') + 1:]))

            if PID == o_id:
                relogio.corrigir_tempo(tempo)
                print("TEMPO CORRIGIDO:", relogio.get_tempo())

        elif PID != id:
            if resp == "eleicao":
                if PID > id:
                    msg = "eleicao"
                    estado = BullyInit()
                else:
                    msg = "OK"
                    estado = BullySub()

        return estado, msg


def main():

    print("Eu sou", PID)

    comunicacao.bind()

    executor = Sistema()

    executor.iniciar_bully()
    on = True

    while on:

        resp = comunicacao.receber()

        if resp and int(resp[:resp.index('/')]) != PID:
            print("recebido:", resp)

        msg = executor.responder(resp)

        if msg:
            if msg != "final":
                comunicacao.enviar(str(PID) + '/' + msg)
                print("enviado:", str(PID) + '/' + msg)
            else:
                on = False

        print("tempo atual:", relogio.get_tempo())
        time.sleep(1)

    relogio.finalizar_relogio()


main()