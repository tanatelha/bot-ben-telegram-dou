GOOGLE_SHEETS_KEY = os.environ["GOOGLE_SHEETS_KEY"] 

GOOGLE_SHEETS_CREDENTIALS = os.environ['GOOGLE_SHEETS_CREDENTIALS']
with open("credenciais.json", mode="w") as arquivo:
    arquivo.write(GOOGLE_SHEETS_CREDENTIALS)
conta = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")

api = gspread.authorize(conta)
planilha = api.open_by_key(f'{GOOGLE_SHEETS_KEY}') 
sheet_inscritos = planilha.worksheet('inscritos')


def identificar_inscritos():
    lista_inicial = []
    inscritos_final = []

    inscritos = sheet_inscritos.col_values(6)
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
