def identificar_inscritos():
    lista_inicial = []
    inscritos_final = []

    inscritos = planilha_inscritos.col_values(6)
    inscritos = list(set(inscritos))
    if '' in inscritos:
        inscritos.remove('')
        lista_inicial.append(inscritos)
    else:
        lista_inicial.append(inscritos)

    # fazendo apenas uma lista
    for sublista in lista_inicial:
        inscritos_final.extend(sublista)

    return inscritos_final
