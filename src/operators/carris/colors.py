#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')))

import requests as re
from bs4 import BeautifulSoup
import utils.logger as logger
import utils.db.operators.db_carris as db_carris

url = 'https://www.carris.pt/viaje/carreiras/{}/'
special_url = {
    '45B': 'https://www.carris.pt/viaje/carreiras/45b-alta-de-lisboa-c-saude-paco-lumiar/',
    '763': 'https://www.carris.pt/viaje/carreiras/763-lumiar-colegio-militar-metro/',
    '71B': 'https://www.carris.pt/viaje/carreiras/71b-colegio-militar-metro-circulacao-b-boavista-b-sta-cruz/',
    '72B': 'https://www.carris.pt/viaje/carreiras/72b-colegio-militar-metro-circulacao-b-sta-cruz-b-boavista/',
    '51E': 'https://www.carris.pt/viaje/carreiras/gloria-restauradores-circulacao-lg-carmo/',
    '52E': 'https://www.carris.pt/viaje/carreiras/12e/', #Ascensores parados
    '53E': 'https://www.carris.pt/viaje/carreiras/12e/', #Ascensores parados
    '54E': 'https://www.carris.pt/viaje/carreiras/12e/' #Ascensores parados
}

def get_color_from_internet(code):
    if code in special_url:
        response = re.get(special_url[code])
    else:
        response = re.get(url.format(code))
    if response.status_code != 200:
        logger.error(f'Falhou a ir buscar a página da carris para a carreira {code}: {response.status_code}.')
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    color = get_color_from_div_simple(soup)
    if color is not None:
        return color
    else:
        return get_color_from_div_multiple(soup)
    
def get_color_from_div_simple(soup):
    divs = soup.find_all("div", {"class": "variant"})
    if len(divs) != 1:
        return None

    return divs[0].attrs['style'].split(':')[1][0:7]

def get_color_from_div_multiple(soup):
    choice = soup.find(id='VariantNumber')
    if choice is None:
        return None

    return choice.attrs['style'].split(':')[1][0:7]

def get_color(db, code):
    color = db_carris.get_color(db, code)
    if color is None:
        logger.warn(f'Falta a cor da carreira {code}, a ir buscar ao site da carris')
        color = get_color_from_internet(code)
        if color is None:
            raise Exception(f'Incapaz de encontrar a cor para a carreira {code}')
        db_carris.set_color(db, code, color)
        logger.info(f'A cor da carreira {code} é {color}.')
    return color