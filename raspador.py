import requests
from bs4 import BeautifulSoup
from datetime import date, time, timedelta
from datetime import datetime

from data_hora import data_hoje, hora_hoje

data_do_dia = data_hoje()

def mensagem():

  finalizacao = f'Para mais informações, <a href="https://www.in.gov.br/servicos/diario-oficial-da-uniao">acesse o site do DOU</a>'

  headers = {'User-Agent': 'Mozilla/5.0'}
  resposta = requests.get('https://www.in.gov.br/servicos/diario-oficial-da-uniao/destaques-do-diario-oficial-da-uniao', params=None, headers=headers)
  site = BeautifulSoup(resposta.content, features="html.parser")
  lista_materias = site.findAll('div', {'class' : 'dou row'}) #parte do site html que tem as matérias

  texto = f'<b>Bom dia, humana!</b> \U0001F31E \N{hot beverage}	\n \nVamos lá para os destaques do <i>Diário Oficial da União</i> de hoje! \n \n<b>{data_do_dia}</b> \n'

  lista = []

  for materia in lista_materias:
    noticia = materia
    data = (noticia.find('p', {'class' : 'date'})).text

    if data == data_do_dia:
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
