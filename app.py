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
sheet_inscricoes = planilha.worksheet('inscricoes')

app = Flask(__name__)


@app.route("/")
def index():
  return "Esse é o site do Ben do Diário Oficial da União"


----------------------------------------------------------------------------------------------------------------------------------------

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

----------------------------------------------------------------------------------------------------------------------------------------
 
# PASSO 4 | TELEGRAM INSCRICOES
@app.route("/bot-ben-telegram", methods=["POST"])
def telegram_bot():
  mensagens = []
  inscricoes =[]
  
  update = request.json 

  ### dados da mensagem
  update_id = update['update_id']
  first_name = update['message']['from']['first_name']
  last_name = update['message']['from']['last_name']
  user_name = update['message']['from']['username']
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

  inscricoes.append([str(date), str(time), first_name, last_name, user_name, sender_id])
  mensagens.append([str(datahora), "recebida", username, first_name, chat_id, message]) # Salvar as mensagens recebidas no sheets
  


  ### definição da mensagem a ser enviada a partir da mensagem recebida

  if message == "start":
    texto_resposta = "Olá, humana! \n \nEu sou o <b>Benjamin do Diário Oficial da União</b>, mas você pode me chamar de <b>Ben do DOU</b>!  Ou apenas Ben... \U0001F916 \n \nPara ter acesso aos destaques do DOU de hoje, basta digitar /manda que eu te envio. \n \nSeja bem-vinda! \U0001F609"

  else:
    texto_resposta = "Olá, humano! \n \nEu sou o <b>Benjamin do Diário Oficial da União</b>, mas você pode me chamar de <b>Ben do DOU</b>! Ou apenas Ben... \U0001F916 \n \nSou um bot criado para enviar diariamente, por meio do Telegram, os destaques do Executivo publicados no <i>Diário Oficial da União</i>. \n \nPara receber as minhas mensagens, basta enviar um /manda que te envio na hora os principais decretos do dia.\n \nEspero que você goste do meu trabalho \U0001F609"


  ### Códigos do telegram para enviar mensagem
    nova_mensagem = {"chat_id": chat_id, "text": texto_resposta, "parse_mode": 'html'}
    resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_TOKEN}/sendMessage", data = nova_mensagem)

    mensagens.append([str(datahora), "enviada", username, first_name, chat_id, texto_resposta])


  ### Atualizando a planilha sheets ss mensagens enviadas
  sheet_inscricoes.append_rows(inscricoes)
  sheet_mensagens.append_rows(mensagens)
  

  return f"Mensagem enviada. Resposta ({resposta.status_code}): {resposta.text}"

----------------------------------------------------------------------------------------------------------------------------------------

# PASSO 5 | TELEGRAM ENVIO DIÁRIO DE MENSAGENS
@app.route("/bot-ben-telegram-envio")

apresentacao = f'<b>Bom dia, humana!</b> \N{sun with face} \n \nVamos lá para os destaques do <i>Diário Oficial da União</i> de hoje! \n \n \N{tear-off calendar} <b>{data_hoje()}</b> \n'
finalizacao = f'Para mais informações, <a href="https://www.in.gov.br/servicos/diario-oficial-da-uniao">acesse o site do DOU</a>'


def telegram_bot_envio():
  resposta = requests.get('https://www.in.gov.br/servicos/diario-oficial-da-uniao/destaques-do-diario-oficial-da-uniao', params=None)
  site = BeautifulSoup(resposta.content, features="html.parser")
  lista_materias = site.findAll('div', {'class' : 'dou row'}) #parte do site html que tem as matérias

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
      
      # montagem texto
      texto_final = apresentacao
      for i in mensagem_destaque_lista:
        texto_final += f'\n \n{i}'

      texto_resposta = f'{texto_final} \n \n {finalizacao}'
    
    else:
      texto_resposta = f'<b>Bom dia, humana!</b> \N{sun with face} \n \nNão tem Destaques do DOU para o dia de hoje! \n \n<i>Pode descansar e fazer outra coisa! \U0001F973</i>'
  
 
  return texto_resposta
  
  
  
  
  
  
  
  
  
  
  
