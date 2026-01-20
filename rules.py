from datetime import datetime, time

HORARIO_INICIO = time(8, 0)
HORARIO_FIM = time(18, 0)
ALMOCO_INICIO = time(12, 0)
ALMOCO_FIM = time(13, 0)
DURACAO_MINUTOS = 30

def data_futura(data_str):
    data = datetime.strptime(data_str, "%Y-%m-%d").date()
    return data >= datetime.now().date()

def horario_comercial(hora_str):
    hora = datetime.strptime(hora_str, "%H:%M").time()
    return (
        HORARIO_INICIO <= hora < HORARIO_FIM and
        not (ALMOCO_INICIO <= hora < ALMOCO_FIM)
    )
