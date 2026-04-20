#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))

import argparse
import argcomplete
import configparser
import utils.logger as logger
import requests
import zipfile
import io
from utils.db.db import db_manager
import utils.db.db_operators as db_operators

properties_file_path = '../../conf/global.properties'

def load_properties():
    global conf
    conf = configparser.ConfigParser()

    path = os.path.dirname(os.path.realpath(__file__))
    properties_file = os.path.join(path, properties_file_path)
    
    if os.path.exists(properties_file):
        conf.read(properties_file)
    else:
        logger.error("No properties file found, please configure the conf/global.properties")
        raise Exception('Missing properties file: ' + properties_file)

def db_connect():
    global db
    db = db_manager(conf['db'])
    db.open()

def db_disconnect():
    db.close()

def parse_options():
    parser = argparse.ArgumentParser('Vai buscar os dados fonte para o mapa de transportes públicos.')

    global operators
    operators = db_operators.get_operator_map(db)
    operators_codes = list(operators.keys())
    parser.add_argument('--operators', '-operadoras', '-o', 
            nargs='+', required=True, choices=operators_codes, help='Operadores a preparar')

    argcomplete.autocomplete(parser)

    return parser.parse_args()

def ensure_path(operator):
    path = build_path(operator)
    if not os.path.isdir(path):
        logger.info("A criar pasta para " + operator)
        os.makedirs(path)
        
def build_path(operator):
    return os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../data/source/' + operator))

def download_zip(operator):
    try:
        url = db_operators.get_source_url(db, operator)
    except Exception as e:
        logger.error(f'Não foi possível buscar o gtfs de {operator['name']}: {str(e)}')
        return
    logger.info(f'A buscar de {url['url']}')
    result = requests.get(url['url'], stream=True)
    if result.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(result.content))
        path = build_path(operator['code'])
        z.extractall(path)
        db_operators.set_operator_source_downloaded(db, operator)
        logger.info(f'Extraído para {path}')
    else:
        logger.warn(f'Falhou. Código de erro: {result.status_code}')

def main():
    load_properties()
    db_connect()
    options = parse_options()
    for code in options.operators:
        ensure_path(code)
        download_zip(operators[code])
    db_disconnect()

main()