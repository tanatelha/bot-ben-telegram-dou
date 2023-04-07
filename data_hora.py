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
