from datetime import datetime
from decimal import Decimal
import json
import mysql.connector

def connect():
    try:
        mySQLConnection = {
            'host': 'classify.ecoloop.com.br',  # Endereço do servidor MySQL
            'user': 'root',  # Nome de usuário do MySQL
            'password': 'Gsilva@2022',  # Senha do MySQL
            'database': 'test',  # Nome do banco de dados
            'port': 18088  # Porta do MySQL (padrão é 3306)
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
