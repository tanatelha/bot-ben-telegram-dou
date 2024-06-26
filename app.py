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

# importanto funcoes de outros arquivos do repositório
from data_hora import data_hoje, hora_hoje
from raspador import mensagem


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



# Criação do site
app = Flask(__name__)


@app.route("/")
def index():
  return "Esse é o site do Ben do Diário Oficial da União"


@app.route("/bot-ben-telegram", methods=["POST"])
def telegram_bot():
  mensagens = []
  inscricoes = []
  descadastrados = []
  
  update = request.json 

  ### dados da mensagem
  update_id = update['update_id']
  first_name = update['message']['from']['first_name']
  sender_id = update['message']['from']['id']
  chat_id = update['message']['chat']['id']
  date = datetime.fromtimestamp(update['message']['date']).date().strftime('%d/%m/%Y')
 
  # calcular horário / converter fuso
  timestamp = update['message']['date']  
  fuso_sao_paulo = pytz.timezone('America/Sao_Paulo') # converter para o fuso horário 'America/Sao_Paulo'
  saopaulo_time = datetime.fromtimestamp(timestamp, fuso_sao_paulo)
  time = saopaulo_time.strftime('%H:%M:%S')

  if 'text' not in update['message']:
    message = 'A mensagem é um conteúdo textual que não é possível compreender.'
  else:
    message = update['message']['text'].lower().strip()
  
  if "username" in update['message']['from']:
    username = f"@{update['message']['from']['username']}"
  else:
    username = f'@ indisponível'

  
  ### definição da mensagem a ser enviada a partir da mensagem recebida
  inscritos = sheet_inscritos.col_values(6)
  print(inscritos)
  
  if message == "/start":
        if str(chat_id) in inscritos:
            print(chat_id)
            texto_resposta = f'Hmmm... \U0001F914 \n \nPelas minhas anotações, <b>você já está inscrita</b> para receber os destaques do Diário Oficial da União! \n \nAgora é só esperar as manhãs para tomar café com os destaques em mãos \U0001F60C \N{hot beverage} \n \nCaso queira acessar um comando específico, clique em "menu" aqui do lado esquerdo da tela'
            nova_mensagem = {"chat_id": chat_id, "text": texto_resposta, "parse_mode": 'html'}
            resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_TOKEN}/sendMessage", data = nova_mensagem)
            mensagens.append([str(date), str(time), "recebida", username, first_name, chat_id, message])
            mensagens.append([str(date), str(time), "enviada", username, first_name, chat_id, texto_resposta])

        else:
            texto_resposta = "Olá, humana! \n \nEu sou o <b>Benjamin do Diário Oficial da União</b>, mas você pode me chamar de <b>Ben do DOU</b>!  Ou apenas Ben... \U0001F916 \n \nSou um bot criado para enviar diariamente, por meio do Telegram, os destaques do Executivo publicados no <i>Diário Oficial da União</i>. \n \n<b>Você acaba de se inscrever para receber os destaques do DOU!</b> \n \nAs mensagens serão enviadas todos os dias a partir das 7h da manhã \U0001F973"
            nova_mensagem = {"chat_id": chat_id, "text": texto_resposta, "parse_mode": 'html'}
            resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_TOKEN}/sendMessage", data = nova_mensagem)
            inscricoes.append([str(date), str(time), first_name, username, sender_id, chat_id, message])
            
            
  elif message == "/exit":
    # data = sheet_inscritos.get_all_values()
      
    data = sheet_inscritos.col_values(6)
    id_procurado = str(chat_id)  # é o mesmo valor que o chat_id calculado lá em cima

    def processo_de_descadrastamento():
        for item in data:
          if item == id_procurado:
            indice = data.index(item) #encontra a posição do item na lista
            linha_encontrada = indice + 1
            sheet_inscritos.update(f"A{linha_encontrada}:Z{linha_encontrada}", [[""] * 26])
            
              # sheet_inscritos.delete_row(linha_encontrada) # dois argumentos: o número da linha a ser excluída e o número de linhas a serem excluídas.
            
            texto = f'Você foi descadastrado e não irá mais receber as minhas mensagens! Que pena, humana! \U0001F622 \n \nCaso deseje voltar a receber os meus trabalhos, basta me mandar "/start" que eu te reinscrevo. \n \nNos vemos por aí \U0001F916'
    
        return texto
    
    texto_resposta = processo_de_descadrastamento()
    nova_mensagem = {"chat_id": id_procurado, "text": texto_resposta, "parse_mode": 'html'}
    resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_TOKEN}/sendMessage", data = nova_mensagem)
    descadastrados.append([str(date), str(time), "descadastrado", username, first_name, chat_id, texto_resposta])

    
  else:
    texto_resposta = f'Olá, humana! \n \nVocê já se inscreveu para receber os destaques do Executivo publicados no <i>Diário Oficial da União</i>. Agora é só esperar os envios das mensagens todo dia de manhã a partir das 7h \U0001F609 \n \nCaso queira acessar um comando específico, clique em "menu" aqui do lado esquerdo da tela'
    nova_mensagem = {"chat_id": chat_id, "text": texto_resposta, "parse_mode": 'html'}
    resposta = requests.post(f"https://api.telegram.org./bot{TELEGRAM_TOKEN}/sendMessage", data = nova_mensagem)
    mensagens.append([str(date), str(time), "recebida", username, first_name, chat_id, message])
    mensagens.append([str(date), str(time), "enviada", username, first_name, chat_id, texto_resposta])
    
 
 
  ### Atualizando a planilha sheets ss mensagens enviadas
  sheet_inscritos.append_rows(inscricoes)
  sheet_mensagens.append_rows(mensagens)
  sheet_descadastrados.append_rows(descadastrados)
    
  print(message)
  print(resposta.text)
  return "ok"





@app.route("/bot-ben-telegram-envio")

def telegram_bot_envio():
    data = data_hoje()
    hora = hora_hoje()
    texto_resposta = mensagem()
    inscritos = sheet_inscritos.col_values(6)
   

    enviadas = []
    for id in inscritos:
        nova_mensagem = {"chat_id": id,
                    "text": texto_resposta,
                    "parse_mode": 'html'}
        resposta_2 = requests.post(f"https://api.telegram.org./bot{TELEGRAM_TOKEN}/sendMessage", data=nova_mensagem)
        #print(resposta_2.text)
        enviadas.append([str(data), str(hora), "enviada", id, texto_resposta])
    
    sheet_enviadas.append_rows(enviadas)

    print(resposta_2.text) 
    return f'{(resposta_2.text)}'
  
  
  
