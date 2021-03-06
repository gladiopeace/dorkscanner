import os
import sys
import requests
import argparse
from random import randint
from functools import partial
from multiprocessing import Pool
from urllib.request import urlopen
from bs4 import BeautifulSoup as bsoup


GREEN, RED, ORANGE, PURPLE, CYAN, WHITE, YELLOW, LIGHTGRAY = '\033[1;32m', '\033[1;31m', '\033[0;33m', '\033[1;35m', '\033[1;36m', '\033[1;37m', '\033[1;33m', '\033[0;37m'
colours = [ORANGE, PURPLE, CYAN, WHITE, YELLOW, LIGHTGRAY, RED]
color = colours[randint(0,6)]
def get_arguments():
    parser = argparse.ArgumentParser(prog='python dorkScanner.py',description='Exemple : python dorkScanner.py -e Bing -p 2 -P 1 -o test.txt -d dorks.txt')
    parser.add_argument('-q', '--query', dest='query', help='Spécifie la recherche sans les guillemets (\'\')')
    parser.add_argument('-e', '--engine', dest='engine', help='Spécifie le moteur de recherche (Google | Bing)')
    parser.add_argument('-p', '--pages', dest='pages', help='Spécifie le nombre de pages (Défaut: 1)')
    parser.add_argument('-P', '--processes', dest='processes', help='Spécifie le nombre de processus (Défaut: 2)')
    parser.add_argument('-o', '--output', dest='output', help=f'Spécifie le nom du fichier de sortie \n(Défaut: {os.getcwd()}/pages/pages.txt)')
    parser.add_argument('-d', '--dork', dest='dork', help=f'Spécifie le fichier contenant les dorks (Défaut: {os.getcwd()}/dorks/dorks.txt)')
    options = parser.parse_args()
    return options


def google_search(query, page):
    counter = 0
    result = []
    print("[!] Les recherches sur google peuvent échouer à cause du captcha")
    if options.dork:
        dorksfile = os.getcwd() + "/dorks/" + options.dork

        try:
            file = open(dorksfile,"r",encoding="utf8", errors='ignore')
            lines = file.readlines()
            for line in lines:
                base_url = 'https://www.google.com/search'
                headers  = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0' }
                params   = { 'q': line, 'start': page * 10 }
                resp = requests.get(base_url, params=params, headers=headers)
                soup = bsoup(resp.text, 'html.parser')
                links  = soup.findAll('cite')
                counter += 1
                print(f'[!] Patientez - Recherche effectuée : {counter}/{len(lines)}',end="\r")
                for link in links:
                    result.append(link.text)
            return result
        except FileNotFoundError:
            print(f'Vérifiez que le fichier {options.dork} se trouve bien dans le dossier /dorks/')
    else:
        base_url = 'https://www.google.com/search'
        headers  = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0' }
        params   = { 'q': query, 'start': page * 10 }
        resp = requests.get(base_url, params=params, headers=headers)
        soup = bsoup(resp.text, 'html.parser')
        links  = soup.findAll('cite')
        for link in links:
            result.append(link.text)
        return result


def bing_search(query, page):
    counter = 0        
    result = []

    if options.dork:
        print(f'[!] La recherche d\'URL peut prendre quelques minutes avec l\'option -d')
        dorksfile = os.getcwd() + "/dorks/" + options.dork
        try:
            file = open(dorksfile,"r", errors='ignore')
            lines = file.readlines()
            for line in lines:
                line = f'"{line}"'
                base_url = 'https://www.bing.com/search'
                headers  = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
                params   = {'q':line, 'first':page * 10 + 1}
                resp = requests.get(base_url, params=params, headers=headers)
                soup = bsoup(resp.text, 'html.parser')
                print('-'*70)
                counter += 1
                links  = soup.findAll('cite')
                print(f'[!] Patientez - Recherche effectuée : {counter}/{len(lines)}',end="\r")
                for link in links:
                    result.append(link.text)
        except FileNotFoundError:
            print(f'Vérifiez que le fichier {options.dork} se trouve bien dans le dossier /dorks/')
    else:
        base_url = 'https://www.bing.com/search'
        headers  = {'User-Agent': 'Mozilla/17.0 (X22; Parrot OS; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0'}
        params   = {'q': query, 'first': page * 10 + 1}
        resp = requests.get(base_url, params=params, headers=headers)
        soup = bsoup(resp.text, 'html.parser')
        links  = soup.findAll('cite')
        for link in links:
            result.append(link.text)
    return result


def search_result(q, engine, pages, processes, result, output):
    blacklist = ['www.facebook.','www.google.','pastebin','vk','gist','github',
                 'udemy','jetbrains','www.youtube.','whatsapp','telegram',
                 'twitter','vuldb', 'tenable', 'exploit-db','stackoverflow'
                 ,'bing','www.w3schools.com','wikipedia','www.cvedetails.com',]

    pagesfolder = os.getcwd() + "/pages/"
    page = pagesfolder + output
    ls = []
    print('-' * 70)
    print(f'Recherche : {q} dans {pages} page(s) sur {engine} avec {processes} processus')
    print('-' * 70)
    print()
    counter = 0
    for range in result:
        try:
            for r in range:
                f = open(page, "a",encoding="utf8", errors='ignore')
                if r not in blacklist and '?' in r and '=' in r:
                    f.write(r + "\n")
                    print(color + '[+] ' + r)
                    counter += 1
            f.close()
        except:
            print('Aucun résultat trouvé')
            exit()
    with open(page, 'r') as f:
        for line in f:
            if line not in ls and '?' in line and '=' in line:
                for i in blacklist:
                    if i in line:
                        break
                ls.append(line)
    with open(page, 'w') as f:
        for line in ls:
            f.write(line)
    print()
    print('-' * 70)
    print(f'Nombre d\'URL: {counter}')
    print('-' * 70)
    print(f'Fichier de sortie crée avec succès : {page}')

def is_internet_available():
    try:
        ping = urlopen('http://www.google.com', timeout=5000)
        return GREEN + "[!] Connexion à Internet : OK !"
    except:
        print(RED + "[!] Connexion à Internet : PAS OK !\n")
        exit()

banner = ''' 

     ____             _     ____                                  
    |  _ \  ___  _ __| | __/ ___|  ___ __ _ _ __  _ __   ___ _ __ 
    | | | |/ _ \| '__| |/ /\___ \ / __/ _` | '_ \| '_ \ / _ \ '__|
    | |_| | (_) | |  |   <  ___) | (_| (_| | | | | | | |  __/ |   
    |____/ \___/|_|  |_|\_\|____/ \___\__,_|_| |_|_| |_|\___|_| 
    
        Made By	: Balgogan (github.com/Balgogan)

'''
options = get_arguments()

def main():
    print(is_internet_available())
    if not options.query and not options.dork:
        query = input('[?] Entrez votre recherche : ')
    else:
        query = options.query
    if not options.engine:
        engine = input('[?] Choisissez votre moteur de recherche (Google | Bing): ')
    else:
        engine = options.engine

    if engine.lower() == 'google':
        target = partial(google_search, query)
    elif engine.lower() == 'bing':
        target = partial(bing_search, query)
    elif engine.lower() == 'duckduckgo' or engine.lower() == 'duck':
        target = partial(duck_search, query)
    else:
        print('[-] L\'option entrée est invalide !...Fermeture du programme....')
        exit()

    if not options.pages:
        pages = 1
    else:
        pages = options.pages

    if not options.processes:
        processes = 2
    else:
        processes = options.processes
    if not options.output:
	    output = "pages.txt"
    else:
        output = options.output
    if not options.dork:
        dork = "dorks.txt"

    with Pool(int(processes)) as p:
        result = p.map(target, range(int(pages)))
    search_result(query, engine, pages, processes, result, output)


print(color + banner)

try:
    main()
    
except KeyboardInterrupt:
    print('\nMerci d\'avoir utilisé ce programme !')
   
except TimeoutError:
    print(RED + '\n[-] Trop de requêtes, Réessayez plus tard....')
    