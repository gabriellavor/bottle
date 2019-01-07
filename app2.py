from bottle import get, post, put,request ,route, run, template,HTTPResponse
import json
from Mysql import Mysql
from bson import json_util
import datetime
from datetime import date, timedelta


#pip install bottle
@route('/localizacao')
def localizacao():
    bd = Mysql()
    retorno = []
    cursor = bd.cursor
    query = ("SELECT  motorista.codigo AS codigo,nome, idade, sexo, tipo_cnh, veiculo_proprio, tipo_veiculo.descricao AS tipo_veiculo_descricao, \
        (SELECT carregado FROM checkin WHERE checkin.codigo_motorista = motorista.codigo order by data DESC LIMIT 1) AS carregado\
         FROM motorista\
         INNER JOIN tipo_veiculo ON (tipo_veiculo.codigo = motorista.tipo_veiculo)")
    bd.query(query)
    resultado = bd.fetchall()

    for dado in resultado:
        retorno.append({
            'codigo': dado[0],
            'name': dado[1],
            'idade': dado[2],
            'sexo': dado[3],
            'tipo_cnh': dado[4],
            'veiculo_proprio':dado[5],  
            'tipo_veiculo_descricao':dado[6],
            'carregado':dado[7],
        })
     
    return retornar(retorno,200)


@route('/veiculo-vazio')
def veiculo_proprio():
    bd = Mysql()
    cursor = bd.cursor
    query = ("SELECT  nome, idade, sexo, tipo_cnh, veiculo_proprio, tipo_veiculo.descricao AS tipo_veiculo_descricao, \
        (SELECT carregado FROM checkin WHERE checkin.codigo_motorista = motorista.codigo order by data DESC LIMIT 1) AS carregado\
        FROM motorista\
        INNER JOIN tipo_veiculo ON (tipo_veiculo.codigo = motorista.tipo_veiculo)\
        WHERE (SELECT carregado FROM checkin WHERE checkin.codigo_motorista = motorista.codigo order by data DESC LIMIT 1) = 0\
    ")
    bd.query(query)
    retorno = []
    resultado = bd.fetchall()
    for dado in resultado:
        retorno.append({
            'name': dado[0],
            'idade': dado[1],
            'sexo': dado[2],
            'tipo_cnh': dado[3],
            'veiculo_proprio':dado[4],  
            'tipo_veiculo_descricao':dado[5],
            'carregado':dado[6],
        })
    
    return retornar(retorno,200)


@route('/veiculo-proprio')
def veiculo_proprio():
    retorno = []
    bd = Mysql()
    cursor = bd.cursor
    query = ("SELECT  count(*) AS qtd FROM motorista WHERE veiculo_proprio = 1")
    bd.query(query)
    
    resultado = bd.fetchall()

    for dado in resultado:
        retorno.append({
            'qtd': dado[0]
        })
    
    return retornar(retorno,200)

@route('/veiculo-terminal')
def veiculo_por_terminal():
    retorno = []
    bd = Mysql()
    cursor = bd.cursor
    data = inicio_fim_semana()

    query = ("SELECT (SELECT COUNT(*)  FROM checkin WHERE Day(data) = Day(NOW())) as dia,\
            (SELECT COUNT(*)  FROM checkin WHERE data between '"+data[0]+"' and '"+data[1]+"') as semana,\
            (SELECT COUNT(*)  FROM checkin WHERE Month(data) = Month(NOW())) as mes\
            FROM checkin LIMIT 1")

    bd.query(query)
    resultado = bd.fetchall()

    for dado in resultado:
        retorno.append({
            'dia': dado[0],
            'semana': dado[1],
            'mes': dado[2],
        })
     
    return retornar(retorno,200)

@route('/lista-tipo')
def lista_tipo():
    retorno = []
    bd = Mysql()
    cursor = bd.cursor
    data = inicio_fim_semana()

    query = ("SELECT 'origem' as tipo,origem.descricao,tipo_veiculo.descricao,count(*) as qtd FROM checkin\
        inner join motorista ON (motorista.codigo = checkin.codigo_motorista)\
        inner join tipo_veiculo ON (tipo_veiculo.codigo = motorista.tipo_veiculo)\
        INNER JOIN local origem ON (origem.codigo = checkin.codigo_origem)\
        GROUP BY origem.descricao,tipo_veiculo.descricao\
        UNION\
        SELECT 'destino' as tipo ,destino.descricao,tipo_veiculo.descricao,count(*) as qtd  FROM checkin\
        inner join motorista ON (motorista.codigo = checkin.codigo_motorista)\
        inner join tipo_veiculo ON (tipo_veiculo.codigo = motorista.tipo_veiculo)\
        INNER JOIN local destino ON (destino.codigo = checkin.codigo_destino)\
        GROUP BY destino.descricao,tipo_veiculo.descricao\
    ")

    bd.query(query)
    
    resultado = bd.fetchall()

    for dado in resultado:
        retorno.append({
            'tipo': dado[0],
            'descricao_local': dado[1],
            'descricao_tipo_veiculo': dado[2],
            'qtd_veiculos': dado[3],
        })
    return retornar(retorno,200)


@put('/atualizar')
def atualizar():
    bd = Mysql()
    cursor = bd.cursor
    post = json.loads(request.body.getvalue().decode('utf-8'))
    #motorista
    codigo = post["codigo"]
    nome = post["nome"]
    idade = post["idade"]
    veiculo_proprio = post["veiculo_proprio"]
    tipo_cnh = post["tipo_cnh"]
    sexo = post["sexo"]
    tipo_veiculo = post["tipo_veiculo"]

    codigo = retorna_motorista_por_codigo(codigo)
    if(codigo != False):
        sql_motorista = """ UPDATE `motorista`
        SET `nome` = %s ,`idade` = %s ,`sexo` = %s ,`veiculo_proprio` = %s ,`tipo_veiculo` = %s ,`tipo_cnh` = %s WHERE codigo = %s"""
        bd.query(sql_motorista,(nome,idade,sexo,veiculo_proprio,tipo_veiculo,tipo_cnh,codigo))
        bd.commit()
        if(cursor.rowcount > 0):
            return retornar('Alterado com sucesso!',200)
        else:
            return retornar('Nenhum registro foi alterado!',200)
        
    else:
        retorno = 'Motorista Informado não existe'
        return retornar(retorno,400)
        

@post('/cadastrar')
def cadastrar():
    bd = Mysql()
    cursor = bd.cursor
    post = json.loads(request.body.getvalue().decode('utf-8'))
    #motorista
    nome = post["nome"]
    idade = post["idade"]
    veiculo_proprio = post["veiculo_proprio"]
    tipo_cnh = post["tipo_cnh"]
    sexo = post["sexo"]
    tipo_veiculo = post["tipo_veiculo"]
    #checkin
    carregado = post["carregado"]
    #local
    origem_descricao = post["origem_descricao"]
    origem_latitude = post["origem_latitude"]
    origem_longitude = post["origem_longitude"]
    destino_descricao = post["destino_descricao"]
    destino_latitude = post["destino_latitude"]
    destino_longitude = post["destino_longitude"]
      
    sql_local = """ INSERT INTO `local`
        (`descricao`, `latitude`, `longitude`) VALUES (%s,%s,%s)"""
    
    sql_motorista = """ INSERT INTO `motorista`
        (`nome`, `idade`, `sexo`, `veiculo_proprio`,`tipo_veiculo`,`tipo_cnh`) VALUES (%s,%s,%s,%s,%s,%s)"""

    sql_checkin = """ INSERT INTO `checkin`
        (`data`, `codigo_origem`, `codigo_destino`, `carregado`,`codigo_motorista`) VALUES (%s,%s,%s,%s,%s)"""

    id_origem = retorna_codigo_local(origem_descricao)
    if(id_origem == False):
        bd.query(sql_local,(origem_descricao,origem_latitude,origem_longitude))
        id_origem = cursor.lastrowid
    id_destino = retorna_codigo_local(destino_descricao)
    
    if(id_destino == False):
        bd.query(sql_local,(destino_descricao,destino_latitude,destino_longitude))
        id_destino = cursor.lastrowid
    id_motorista = retorna_motorista(nome)
    
    if(id_motorista == False):
        bd.query(sql_motorista,(nome,idade,sexo,veiculo_proprio,tipo_veiculo,tipo_cnh))
        id_motorista = cursor.lastrowid
    bd.query(sql_checkin,(datetime.datetime.now(),id_origem,id_destino,carregado,id_motorista))
    id_checkin = cursor.lastrowid
    
    bd.commit()
    if(id_checkin):
        return retornar('sucesso',200)
    else:
        return retornar('erro',400)

def retornar(retorno,status):
    headers = {'Content-type': 'application/json'}
    theBody = {'retorno': retorno}
    return HTTPResponse(status=status, body=theBody,headers=headers)

def retorna_codigo_local(descricao):
    bd = Mysql()
    cursor = bd.cursor
    query = ("SELECT  codigo FROM local Where descricao = '"+str(descricao)+"'")
    bd.query(query)
    resultado = bd.fetchall()
    
    for dado in resultado:
        return dado[0]
    return False

def retorna_motorista(nome):
    bd = Mysql()
    cursor = bd.cursor
    query = ("SELECT  codigo FROM motorista Where nome = '"+str(nome)+"'")
    bd.query(query)
    resultado = bd.fetchall()
    
    for dado in resultado:
        return dado[0]
    return False

def retorna_motorista_por_codigo(codigo):
    bd = Mysql()
    cursor = bd.cursor
    query = ("SELECT  codigo FROM motorista Where codigo = '"+str(codigo)+"'")
    bd.query(query)
    resultado = bd.fetchall()
    
    for dado in resultado:
        return dado[0]
    return False

def inicio_fim_semana():
    d = date.today()

    if(d.weekday() == 6):
        ini = 0
        fim = 6
    else:
        ini = (d.weekday()+1) * -1
        fim = 5-d.weekday()
    data = (str(date.today() + timedelta(days=ini)) +' 00:00:00',str(date.today() + timedelta(days=fim)) +' 23:59:59') 
    
    return data

if __name__ == '__main__':
    run(host='localhost', port=8080)
