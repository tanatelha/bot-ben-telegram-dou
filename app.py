# bibliotecas que já vem com python
import os #biblioteca para ver chaves em ambiente virtual


# bibliotecas externas: import em ordem alfabética e depois froms em ordem alfabética
import gspread
import pytz
import requests
from flask import Flask, request
from bs4 import BeautifulSoup
from datetime import date, time, timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
from oauth2client.service_account import ServiceAccountCredentials 

# variáveis de ambiente
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_ADMIN_ID = os.environ["TELEGRAM_ADMIN_ID"]

GOOGLE_SHEETS_KEY = os.environ["GOOGLE_SHEETS_KEY"] 

GOOGLE_SHEETS_CREDENTIALS = os.environ['GOOGLE_SHEETS_CREDENTIALS']
with open("credenciais.json", mode="w") as arquivo:
    arquivo.write(GOOGLE_SHEETS_CREDENTIALS)
conta = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")

api = gspread.authorize(conta)
planilha = api.open_by_key(f'{GOOGLE_SHEETS_KEY}') 
sheet_mensagens = planilha.worksheet('mensagens')
sheet_enviadas = planilha.worksheet('enviadas')
sheet_inscritos = planilha.worksheet('inscritos')
sheet_descadastrados = planilha.worksheet('descadastrados')





app = Flask(__name__)

@app.route("/")
def index():
  return "Esse é o site do Ben do Diário Oficial da União"


#----------------------------------------------------------------------------------------------------------------------------------------

# PASSO 1 | Descobrir o dia e transformar a data no formato do DOU

def data_hoje():

  data = date.today()
  dia = data.day

  if dia < 10: 
    dia = str(dia)
    dia = '0'+dia
  else:
    dia = str(dia)

  mes = data.month

  if mes < 10:
    mes = str(mes)
    mes = '0'+mes
  else:
    mes = str(mes)

  ano = data.year
  ano = str(ano)

  data_final = (dia)+'/'+(mes)+'/'+(ano)

  return data_final


def hora_hoje():
  fuso_horario = pytz.timezone('America/Sao_Paulo')   # define o fuso horário
  hora_atual_fuso = datetime.now(fuso_horario)   # obtem a hora atual com o fuso horário definido
  hora_atual_fuso_formatada = hora_atual_fuso.strftime('%H:%M:%S')  # converte a hora atual em uma string formatada
  return hora_atual_fuso_formatada

#----------------------------------------------------------------------------------------------------------------------------------------

# PASSO 2 |

# produção da mensagem
def mensagem():

  # fazer a raspagem e identificar o texto final do dia

  finalizacao = f'Para mais informações, <a href="https://www.in.gov.br/servicos/diario-oficial-da-uniao">acesse o site do DOU</a>'

  resposta = requests.get('https://www.in.gov.br/servicos/diario-oficial-da-uniao/destaques-do-diario-oficial-da-uniao', params=None)
  site = BeautifulSoup(resposta.content, features="html.parser")
  lista_materias = site.findAll('div', {'class' : 'dou row'}) #parte do site html que tem as matérias

  texto = f'<b>Bom dia, humana!</b> \U0001F31E	\n \nVamos lá para os destaques do <i>Diário Oficial da União</i> de hoje! \n \n<b>{data_hoje()}</b> \n'

  lista = []

  for materia in lista_materias:
    noticia = materia
    data = (noticia.find('p', {'class' : 'date'})).text

    if data == data_hoje():
      data = (noticia.find('p', {'class' : 'date'})).text
      pasta = noticia.find('p').text
      manchete = noticia.find('a').text
      link = noticia.find('a').get('href')

      manchete_item = f"\N{card index dividers} <b>{pasta}</b> \n{manchete} | <a href='{link}'>Acesse aqui a decisão</a> "
      lista.append(manchete_item)

  if lista:
    for item in lista:
      texto += f'{item} \n \n'
      texto_resposta = texto

  if not lista:
    texto_resposta = f'<b>Bom dia, humana!</b> \U0001F31E \n \nNão tem Destaques do DOU para o dia de hoje! \n \n<i>Pode descansar e fazer outra coisa! \U0001F973</i>'

  return texto_resposta


# identificar os destinatários
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



#----------------------------------------------------------------------------------------------------------------------------------------



# PASSO 4 | TELEGRAM INSCRICOES
@app.route("/bot-ben-telegram", methods=["POST"])
def telegram_bot():
  mensagens = []
  inscricoes = []
  descadastrados = []
  
  update = request.json 

  ### dados da mensagem
  update_id = update['update_id']
  first_name = update['message']['from']['first_name']
  last_name = update['message']['from']['last_name']
  sender_id = update['message']['from']['id']
  chat_id = update['message']['chat']['id']
  date = datetime.fromtimestamp(update['message']['date']).date().strftime('%d/%m/%Y')
  time = datetime.fromtimestamp(update['message']['date']).time()
  
  if 'text' not in update['message']:
    message = 'A mensagem é um conteúdo textual que não é possível compreender.'
  else:
    message = update['message']['text'].lower().strip()
  
  if "username" in update['message']['from']:
    username = f"@{update['message']['from']['username']}"
  else:
    username = f'@ indisponível'

    
  # salvando as mensagens no sheet  
  if message == "/start":  
    inscricoes.append([str(date), str(time), first_name, last_name, username, sender_id, chat_id, message])
    mensagens.append([str(date), str(time), "recebida", username, first_name, chat_id, message])
    
  else:
    mensagens.append([str(date), str(time), "recebida", username, first_name, chat_id, message]) 
  


  ### definição da mensagem a ser enviada a partir da mensagem recebida

  if message == "/start":
    texto_resposta = "Olá, humana! \n \nEu sou o <b>Benjamin do Diário Oficial da União</b>, mas você pode me chamar de <b>Ben do DOU</b>!  Ou apenas Ben... h\U0001F916 \n \nSou um bot criado para enviar diariamente, por meio do Telegram, os destaques do Executivo publicados no <i>Diário Oficial da União</i>. \n \nVocê acaba de se inscrever para receber os destaques do DOU! As mensagens serão enviadas todos os dias a partir das 7h da manhã. \n \nSeja bem-vinda! \U0001F609"
    
    nova_mensagem = {"chat_id": chat_id, "text": texto_resposta, "parse_mode": 'html'}
    resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_TOKEN}/sendMessage", data = nova_mensagem)

    mensagens.append([str(date), str(time), "inscrito", username, first_name, chat_id, texto_resposta])
  

  elif message == "/descadrastar":
    data = sheet_inscritos.get_all_values()
    id_procurado = update['message']['chat']['id']  # é o mesmo valor que o chat_id calculado lá em cima

    def processo_de_descadrastamento():
        linha_encontrada = None

        for i, row in enumerate(data):
          if row[5] == id_procurado:
            linha_encontrada = i+1    # índice da linha no sheet começa com 0, então adiciona-se 1 ao índice da lista

        if linha_encontrada:
          sheet_inscritos.delete_row(linha_encontrada)
        
        texto_resposta = f'Você foi descadrastado!'

        return texto_resposta
    
    texto_saida = processo_de_descadrastamento()
    
    nova_mensagem = {"chat_id": id_procurado, "text": texto_saida, "parse_mode": 'html'}
    resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_TOKEN}/sendMessage", data = nova_mensagem)
    print(resposta.text)
    
    descadastrados.append([str(date), str(time), "descadastrado", username, first_name, chat_id, texto_resposta])

    
    
  else:
    texto_resposta = "Olá, humano! \n \nVocê já se inscreveu para receber os destaques do Executivo publicados no <i>Diário Oficial da União</i>. Agora é só esperar os envios das mensagens todo dia de manhã a partir das 7h \U0001F609"
    
    nova_mensagem = {"chat_id": chat_id, "text": texto_resposta, "parse_mode": 'html'}
    resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_TOKEN}/sendMessage", data = nova_mensagem)

    mensagens.append([str(date), str(time), "enviada", username, first_name, chat_id, texto_resposta])
    
    
    
 
  ### Atualizando a planilha sheets ss mensagens enviadas
  sheet_inscritos.append_rows(inscricoes)
  sheet_mensagens.append_rows(mensagens)
  sheet_descadastrados.append_rows(descadastrados)

  print(resposta.text)
  return "ok"

#----------------------------------------------------------------------------------------------------------------------------------------

# PASSO 5 | TELEGRAM ENVIO DIÁRIO DE MENSAGENS
@app.route("/bot-ben-telegram-envio")

def telegram_bot_envio():
    data = data_hoje()
    hora = hora_hoje()
    texto_resposta = mensagem()
    inscritos = identificar_inscritos()
    
    update = request.json
    first_name = update['message']['from']['first_name']
    last_name = update['message']['from']['last_name']
    if "username" in update['message']['from']:
        username = f"@{update['message']['from']['username']}"
    else:
        username = f'@ indisponível'
    

    enviadas = []
    for id in inscritos:
        nova_mensagem = {"chat_id": id,
                    "text": texto_resposta,
                    "parse_mode": 'html'}
        resposta_2 = requests.post(f"https://api.telegram.org./bot{TELEGRAM_TOKEN}/sendMessage", data=nova_mensagem)
        #print(resposta_2.text)
        enviadas.append([str(data), str(hora), "enviada", id, first_name, last_name, username, texto_resposta])
    
    sheet_enviadas.append_rows(enviadas)

    print(resposta_2.text) 
    return f'{(resposta_2.text)}'
  
  
  
