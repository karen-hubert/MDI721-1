#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 18:53:45 2020

@author: KarenHubert
"""


import unittest
import requests
from bs4 import BeautifulSoup
import json
from multiprocessing import Pool

URL_PAGE2 = "https://kim.fspot.org/cours/page2.html"
URL_PAGE3 = "https://kim.fspot.org/cours/page3.html"

# 1) Ecrire une fonction get_prices_from_url() qui extrait des informations à partir des 2 pages ci-dessus.
# Exemple get_prices_from_url(URL_PAGE2) doit retourner :
# {'Personal': {'price': '$5', 'storage': '1GB', 'databases': 1},
#  'Small Business': {'price': '$25', 'storage': '10GB', 'databases': 5},
#  'Enterprise': {'price': '$45', 'storage': '100GB', 'databases': 25}}

def get_prices_from_url(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="html.parser")
    if url == 'https://kim.fspot.org/cours/page2.html':
        classe = 'pure-u-1 pure-u-md-1-3'
    else: 
        classe = 'pure-u-1 pure-u-md-1-4'
    prices = {}
    for div_tags in soup.findAll('div', attrs={'class': classe}):
   
        t = div_tags.find('h2')
   
        row = {}
        span = div_tags.find('span')
        index  = span.text.find('$')
        index2  = span.text.find(' ', index)
        prix = span.text[index : index2]
        row['price'] = prix
    
   
        li = div_tags.findAll('li')
        
        index  = li[3].text.find(' ')
        row['storage'] = li[3].text[:index]
   
        index  = li[4].text.find(' ')
        row['databases'] = int(li[4].text[:index])
    
        prices[t.text] = row
    
    return prices



# 2) Ecrire une fonction qui extrait des informations sur une bière de beowulf
# Exemple URL: https://www.beerwulf.com/fr-fr/p/bieres/brouwerij-t-verzet-super-noah.33

def extract_beer_infos(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content)

    #Name
    div_tag_1 = soup.find('div', attrs={'class': 'product-detail-info-title'})
    h1 = div_tag_1.find('h1')
    
    #Prix
    span_prix = soup.find('span', attrs={'class': 'price'})
    
    #note  
    span_note = soup.find('span', attrs={'class': 'label-stars'})
    
    
    #Volume
    div_tag_2 = soup.find('div', attrs={'class': 'product-subtext'})
    span = div_tag_2.find('span')
    index_deb = span.text.find('|', 15)
    index_fin = span.text.find('cl')
    volume = span.text[index_deb + 2 : index_fin-1]
    if volume =='33':
        volume = int(volume)
    else: 
        volume = volume[-2: ]
        volume = int(volume)
        
    
    infos = {
        'name': h1.text,
        'note': span_note.text,
        'price': span_prix.text,
        'volume': volume,
    }
    return infos


# Cette URL retourne un JSON avec une liste de bières
URL_BEERLIST_AUTRICHE = "https://www.beerwulf.com/fr-FR/api/search/searchProducts?country=Autriche&container=Bouteille"

# 3) Ecrire une fonction qui prend l'argument "url" retourne les informations sur une liste de bière via l'API de beowulf.
# Cette fonction doit retourner la liste des informations obtenues par la fonction extract_beer_infos() définie ci-dessus.
# Chercher comment optimiser cette fonction en utilisant multiprocessing.Pool pour paralléliser les accès web.
#
# Exemple de retour :
# [{'name': 'Engelszell Benno', 'note': 70, 'price': 4.29, 'volume': 33}
#  {'name': 'Engelszell Trappisten Weiße', 'note': 70, 'price': 3.39, 'volume': 33}
#  {'name': 'Engelszell Gregorius', 'note': 70, 'price': 4.49, 'volume': 33}
#  {'name': 'Bevog Rudeen Black IPA', 'note': 80, 'price': 4.49, 'volume': 33}
#  {'name': 'Bevog Tak Pale Ale', 'note': 70, 'price': 2.79, 'volume': 33}
#  {'name': 'Brew Age Affenkönig', 'note': 70, 'price': 3.49, 'volume': 33}
#  {'name': 'Stiegl Goldbraü', 'note': 70, 'price': 2.49, 'volume': 33}
#  {'name': 'Stiegl Columbus 1492', 'note': 70, 'price': 2.49, 'volume': 33}
#  {'name': 'Brew Age Hopfenauflauf', 'note': 70, 'price': 2.99, 'volume': 33}]


def extract_beer_list_infos(url):
    # Collecter les pages de bières à partir du JSON
    beer_pages = []
    
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="html.parser")
    js = json.loads(soup.text)
    l = js['items']
    
    

    
    # Sequential version (slow):
    beers = []
    
    
    for i in range(len(l)):
        beer_pages.append('https://www.beerwulf.com' + l[i]['contentReference'])
    
    for i in range(len(beer_pages)):
        infos = extract_beer_infos(beer_pages[i])
        beers.append(infos)

        
    # Parallel version (faster):
    beers_2 = []      
    with Pool() as pool:
        beers_2 = pool.map(extract_beer_infos, beer_pages)
        
        
    return beers_2


class Lesson3Tests(unittest.TestCase):
    def test_01_get_prices_from_url_page2(self):
        prices = get_prices_from_url(URL_PAGE2)
        # We should have found 3 products:
        self.assertIsInstance(prices, dict)
        self.assertEqual(len(prices), 3)
        self.assertIn('Personal', prices)
        self.assertIn('Small Business', prices)
        self.assertIn('Enterprise', prices)

        personal = prices['Personal']
        self.assertIn('price', personal)
        self.assertIn('storage', personal)
        self.assertIn('databases', personal)
        self.assertEqual(personal['price'], '$5')
        self.assertEqual(personal['storage'], '1GB')
        self.assertEqual(personal['databases'], 1)

    def test_02_get_prices_from_url_page3(self):
        prices = get_prices_from_url(URL_PAGE3)
        self.assertIsInstance(prices, dict)
        self.assertEqual(len(prices), 4)
        self.assertEqual(
            prices['Privilege'],
            {'databases': 100, 'price': '$99', 'storage': '1TB'}
        )

    def test_03_extract_beer_list_infos(self):
        infos = extract_beer_list_infos(URL_BEERLIST_AUTRICHE)
        # >Il y a 9 bières autrichiennes :
        self.assertIsInstance(infos, list)
        self.assertEqual(len(infos), 9)
        # toutes ont 33cl :
        for beer in infos:
            self.assertEqual(beer['volume'], 33)


def run_tests():
    test_suite = unittest.makeSuite(Lesson3Tests)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)


if __name__ == '__main__':
    run_tests()

