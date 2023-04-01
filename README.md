# Ben do Diário Oficial da União
O bot Ben do Diário Oficial da União ou Ben do DOU, como ele se autodenominou, é um projeto final da aula de Algoritmos de Automação do Master em Jornalismo de Dados, Automação e Data Storytelling do Insper. O objetivo do robô é informar, diariament,e quais são os destaques do DOU, disponíveis [neste link](https://www.in.gov.br/servicos/diario-oficial-da-uniao/destaques-do-diario-oficial-da-uniao).

## Composição
Para utilizar esse robô, você irá precisar de alguns processos:
* **BotFather:** é uma ferramenta do Telegram para criação de bot. Para car continuidade, é só acessar o site e seguir as orientações. Quando o robô for criado, o Telegram irá te enviar um token. É necessário salvar esse código, pois é com ele que você irá acessar a API do Telegram para enviar os comandos para o seu bot | [Acesso](https://t.me/botfather)
* **Google Sheets:** Para usar o sheets, é necessário pedir acesso ao Google, que pode ser feito [neste link](https://console.cloud.google.com/). O resultado final será dois conteúdos: um e-mail genérico do Google, que será usado para você compartilhar a planilha do sheets com ele, e uma chave de acesso, enviada por meio de um arquivo .json 
* **Render:** é uma plataforma de nuvem, em que podemos usar para colocar o código e automatizar seu funcionamento. No Ben, essa foi a ferramenta utilizada, mas você pode escolher a de sua preferência

## Arquivos
* **requirements.txt:** esse arquivo de texto possui todas as bibliotecas que precisam ser instaladas para rodar o código dentro da nuvem
* **data_hoje.py:** é um py com uma função que coleta o dia e formata do jeito que é solicitado para raspar o DOU
* **raspador.py**: é o raspador do site do DOU oficial
* **telegram.py**: arquivo final com os códigos do robô

## setWebhook
É um método disponível na API do Telegram que permite a configuração de uma URL para receber atualizações do bot de forma assíncrona, em vez de usar o método getUpdates que faz com que o bot precise verificar periodicamente se há atualizações. Quando você configura um webhook, o Telegram enviará uma solicitação HTTP POST para a URL que você especificou sempre que houver uma atualização para o seu bot.

Para fazer essa configuração, você precisa rodar o seguinte código:
```
import getpass            
import requests

token = getpass.getpass()

dados = {"url": "https://bot-ben-telegram-dou.onrender.com"}  # colocar aqui o site do Web Service criado no Render
resposta = requests.post(f"https://api.telegram.org/bot{token}/setWebhook", data = dados)
print(resposta.text)
```

A biblioteca getpass é uma biblioteca que permite com que você use dados pessoais em um código. Ao rodar, irá aparecer um espaço, onde você irá adicionar o token do seu robô no Telegram. 
