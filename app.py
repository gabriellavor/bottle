from bottle import get, post, request ,route, run, template,HTTPResponse
import json
from pymongo import MongoClient
from bson import json_util
import datetime

#pip install bottle
@route('/localizacao')
def localizacao():
    cliente = MongoClient('localhost', 27017)
    banco = cliente.truckpad
    checkin = banco.checkin
  
    retorno = []
    for x in checkin.find({},{'_id':0}):
        retorno.append(
            {
                'nome' : x['nome'],
                'idade' : x['idade'],
                'sexo' : x['sexo'],
                #'carregado' : x['carregado'],
                'tipo_cnh' : x['tipo_cnh'],
                'tipo_veiculo_codigo': x['tipo_veiculo_codigo'],
                'tipo_veiculo_descricao': x['tipo_veiculo_descricao'],
                'veiculo_proprio': x['veiculo_proprio']
                
            }
            
        )
        
    return retornar(retorno,200)


@route('/cadastrar')
def cadastrar():
    cliente = MongoClient('localhost', 27017)
    banco = cliente.truckpad
    checkin = banco.checkin
    mydict =  {
        'nome':'Gabriel Lavor',
        'idade':10,        
        'tipo_cnh':'B',
        'tipo_veiculo_codigo':2,
        'tipo_veiculo_descricao':'Truck',
        'veiculo_proprio':False,
        'sexo':'M',
        'checkin':[
            {
                'carregado':True,
                'origem':'Extra',
                'latitude_origem':-23.5555,
                'longitude_origem':-57.6644,
                'destino':'Mercearia',
                'latitude_destino':-20.5555,
                'longitude_destino':-50.6644,
                'data': datetime.datetime.now()
            },
            {
                'carregado':False,
                'origem':'Extra 2',
                'latitude_origem':-23.5555,
                'longitude_origem':-57.6644,
                'destino':'Mercearia 2',
                'latitude_destino':-20.5555,
                'longitude_destino':-50.6644,
                'data': datetime.datetime.now()
            }
        ]
        
    }
    retorno = checkin.insert_one(mydict)
    if(retorno.inserted_id):
        return retornar('sucesso',200)
    else:
        return retornar('erro',400)

def retornar(retorno,status):
    headers = {'Content-type': 'application/json'}
    theBody = {'retorno': retorno}
    return HTTPResponse(status=status, body=theBody,headers=headers)

if __name__ == '__main__':
    run(host='localhost', port=8080)
