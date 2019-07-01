import time
from threading import *

TESTE = False
_tempo = 0
_on = False
_print_lock = Lock()


def _rodar_relogio():
    global _tempo
    global _on

    while _on:
        _tempo += 1
        time.sleep(0.5)


def iniciar_relogio():
    global _on

    _on = True
    t = Thread(target=_rodar_relogio)
    t.daemon = True
    t.start()


def get_tempo():
    return _tempo


def corrigir_tempo(mod):
    global _tempo

    _tempo += mod


def finalizar_relogio():
    global _on
    _on = False


