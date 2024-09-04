from datetime import datetime
from decimal import Decimal
import json
import mysql.connector

def connect():
    try:
        mySQLConnection = {
            'host': 'engenharia-tcc.c7k8ci6qg68l.us-east-2.rds.amazonaws.com',  # Endereço do servidor MySQL
            'user': 'usuariotodos',  # Nome de usuário do MySQL
            'password': 'eLoGgDoGPYNLKmNpwcnc',  # Senha do MySQL
            'database': 'tccfacul',  # Nome do banco de dados
            'port': 3306  # Porta do MySQL (padrão é 3306)
        }
        return mysql.connector.connect(**mySQLConnection)
    except Exception as ex:
        print('FALHA NA CONEXÃO COM O MySQL: ', ex)

def sqlSelectDict(sql: str, args=()):
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(sql, args)
        headers = [x[0] for x in cursor.description]
        rows = cursor.fetchall()
        data = []
        for row in rows:

            item = {}
            for col, name in enumerate(headers):
                valor = row[col]
                if isinstance(valor, Decimal):
                    item[name] = float(valor)
                elif isinstance(valor, datetime):
                    item[name] = valor.isoformat()
                else:
                    item[name] = valor

            data.append(item)
        cursor.close()
    finally:
        if cnx is not None:
            cnx.close()
    return data


def sqlExecute(sql: str, args=()):
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(sql, args)
        count = cursor.rowcount
        newid = cursor.lastrowid
        cnx.commit()
    except Exception as ex:
        raise ex
    finally:
        if cnx is not None:
            cnx.close()
    return count, newid


def sqlSelect(sql: str, args=()):
    cnx = connect()
    try:
        cursor = cnx.cursor()
        cursor.execute(sql, args)
        result = cursor.fetchall()
        cursor.close()
    finally:
        if cnx is not None:
            cnx.close()

    return result
