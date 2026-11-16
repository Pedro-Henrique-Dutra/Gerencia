def transformador_prioridade_num_texto(valor_inteiro):
    if valor_inteiro == 0:
        return "Baixa"
    elif valor_inteiro == 1:
        return "Media"
    elif valor_inteiro == 2:
        return "Alta"

def transformador_prioridade_texto_num(texto):
    if texto == "Baixa":
        return 0
    elif texto == "Media":
        return 1
    elif texto == "Alta":
        return 2

Prioridades = {
    0: "Baixa",
    1: "Média",
    2: "Alta",
    3: "Urgente"
}