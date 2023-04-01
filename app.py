# bibliotecas que já vem com python
import os #biblioteca para ver chaves em ambiente virtual


# bibliotecas externas: import em ordem alfabética e depois froms em ordem alfabética
import gspread
import requests
from flask import Flask, request
from bs4 import BeautifulSoup
from datetime import date, time, timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
from oauth2client.service_account import ServiceAccountCredentials 

# variáveis de ambiente
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"] 

GOOGLE_SHEETS_KEY = os.environ["GOOGLE_SHEETS_KEY"] 

GOOGLE_SHEETS_CREDENTIALS = os.environ['GOOGLE_SHEETS_CREDENTIALS']
with open("credenciais.json", mode="w") as arquivo:
  arquivo.write(GOOGLE_SHEETS_CREDENTIALS)
conta = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json")

api = gspread.authorize(conta)
planilha = api.open_by_key(f'{GOOGLE_SHEETS_KEY}') 
sheet_mensagens = planilha.worksheet('mensagens')

app = Flask(__name__)


@app.route("/")
def index():
  return "Esse é o site do Ben do Diário Oficial da União"






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


# PASSO 2 | Entrar no site do Diário Oficial da União

resposta = requests.get('https://www.in.gov.br/servicos/diario-oficial-da-uniao/destaques-do-diario-oficial-da-uniao', params=None)
site = BeautifulSoup(resposta.content, features="html.parser")
lista_materias = site.findAll('div', {'class' : 'dou row'}) #parte do site html que tem as matérias

### Criando a função que vai raspar o site do DOU e me devolver uma lista em que cada item é matéria daquele dia com suas informações
def mensagem_destaque():
  mensagem_destaque_lista = []
  
  for materia in lista_materias:
    noticia = materia
    data = (noticia.find('p', {'class' : 'date'})).text
  
    if data == data_hoje():
      pasta = noticia.find('p').text
      manchete = noticia.find('a').text
      link = noticia.find('a').get('href')

      manchete_item = f"\N{card index dividers} <b>{pasta}</b> \n{manchete} | <a href='{link}'>Acesse aqui a decisão</a> "
      mensagem_destaque_lista.append(manchete_item)

  return mensagem_destaque_lista

# PASSO 3 | Criar as partes do texto que vão compor a mensagem final a ser enviada no Telegram

apresentacao = f'<b>Bom dia, humana!</b> \N{sun with face} \n \nVamos lá para os destaques do <i>Diário Oficial da União</i> de hoje! \n \n \N{tear-off calendar} <b>{data_hoje()}</b> \n'
finalizacao = f'Para mais informações, <a href="https://www.in.gov.br/servicos/diario-oficial-da-uniao">acesse o site do DOU</a>'

# PASSO 4 | TELEGRAM
@app.route("/bot-ben-telegram", methods=["GET"])
def telegram_bot():
  mensagens = []
  update = request.json 

  ### dados da mensagem
  update_id = update['update_id']     
  first_name = update['message']['from']['first_name']
  sender_id = update['message']['from']['id']
  chat_id = update['message']['chat']['id']

  if 'text' not in update['message']:
    message = 'A mensagem é um conteúdo textual que não é possível compreender.'
  else:
    message = update['message']['text'].lower().strip()

  datahora = datetime.fromtimestamp(update["message"]["date"])

  if "username" in update['message']['from']:
    username = f" @{update['message']['from']['username']}"
  else:
    username = ""

  mensagens.append([str(datahora), "recebida", username, first_name, chat_id, message]) # Salvar as mensagens recebidas no sheets



  ### definição da mensagem a ser enviada a partir da mensagem recebida

  if message == "/start":
    texto_resposta = 'Olá, humana! \n \nEu sou o <b>Benjamin do Diário Oficial da União</b>, mas você pode me chamar de <b>Ben do DOU</b>!  Ou apenas Ben... \U0001F916 \n \nPara ter acesso aos destaques do DOU de hoje, basta digitar /manda que eu te envio. \n \n Seja bem-vinda! \N{winking face}'

  elif message == "/manda":
    destaque = mensagem_destaque()
    texto_final = apresentacao
    for i in destaque:
      texto_final = f'{texto_final} \n \n{i}'

    texto_resposta = f'{texto_final} \n \n {finalizacao}'

  else:
    texto_resposta = "Olá, humano! \n \nEu sou o <b>Benjamin do Diário Oficial da União</b>, mas você pode me chamar de <b>Ben do DOU</b>! Ou apenas Ben... \U0001F916 \n \nSou um bot criado para enviar diariamente, por meio do Telegram, os destaques do Executivo publicados no <i>Diário Oficial da União</i>. \n \nPara receber as minhas mensagens, basta enviar um /manda que te envio na hora os principais decretos do dia.\n \nEspero que você goste do meu trabalho \N{winking face}"


    ### Códigos do telegram para enviar mensagem
    nova_mensagem = {"chat_id": chat_id, "text": texto_resposta, "parse_mode": 'html'}
    requests.post(f"https://api.telegram.org./bot{TELEGRAM_TOKEN}/sendMessage", data = nova_mensagem)

    mensagens.append([str(datahora), "enviada", username, first_name, chat_id, texto_resposta])


  ### Atualizando a planilha sheets ss mensagens enviadas
  sheet_mensagens.append_rows(mensagens)
  
  return "ok"
