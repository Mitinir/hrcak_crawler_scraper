# -*- coding: utf-8 -*-
"""
Created on Sat May  2 17:19:15 2020

@author: Ivan B.
"""
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse
import urllib.request
import re
import requests
import time

# =============================================================================
# downloadInfo sa stranice časopisa skida listu njegovih brojeva.
# =============================================================================
def downloadInfo(casopis):
    listaBrCas = []
    c = urlopen(casopis).read()
    s = BeautifulSoup(c, features="lxml")
    table = s.find_all('table')[-1:][0]
    hrefs = table.find_all('a')
    for link in hrefs:
        r = {}
        r['link'] = 'https://hrcak.srce.hr' + link['href']
        r['name'] = list(link.children)[1].text
        r['name'] = re.sub(r"\s+", ' ', r['name'], flags=re.UNICODE).strip()
        listaBrCas.append(r)
    print("Download popisa brojeva časopisa gotov.")
    return listaBrCas


# =============================================================================
# downloadHr/EngArchive vraća listu key/value parova (imelinkova), što su
# linkovi na individualne članke u broju.
# =============================================================================
def downloadHrArchive(link):
    archiveHr = []
    c = urlopen(link).read()
    s = BeautifulSoup(c, features="lxml")
    archives = s.find_all('a', 'toc')
    hrClanci = s.find_all('tr', 'bg-even')
    for it in archives:
        h = {}
        if it.parent.parent in hrClanci:
            h['name'] = it.text.replace("\n\t\t", "").strip()
            h['link'] = 'https://hrcak.srce.hr' + it['href']
            archiveHr.append(h)
    print("Download liste hrvatskih članaka gotov za ovaj broj.")
    return archiveHr

def downloadEngArchive(link):
    archiveEng = []
    c = urlopen(link).read()
    s = BeautifulSoup(c, features="lxml")
    archives = s.find_all('a', 'toc')
    engClanci = s.find_all('tr', 'bg-odd')
    for it in archives:
        h = {}
        if it.parent.parent in engClanci:
            h['name'] = it.text.replace("\n\t\t", "").strip()
            h['link'] = 'https://hrcak.srce.hr' + it['href']
            archiveEng.append(h)
    print("Download liste engleskih članaka gotov za ovaj broj.")
    return archiveEng


# =============================================================================
# Ovo u mainu pokrecemo prvo, zadavsi mu link na casopis. Izvadit ce linkove
# ka hrvatskom jeziku. Note: u fajl zapisuje i znak za newline, kojeg cemo 
# kasnije morati replaceati. Nakon nje je funkcija za isto, ali na 
# ostalim jezicima.
# Nema veze što nije svaki članak u ENG na engleskom, jer ćemo u kasnijim
# funkcijama skippati htmlice koje u sebi nemaju 'Sažetak' ili w/ever.
# =============================================================================
def createHtmlURLtxtHR(casopisLink):
    brojevi = downloadInfo(casopisLink)
    file = open("HTMLlinkoviHR.txt", "w")
    listaImenaBrojeva = []    
    listaLinkovaBrojeva = []
    temp = []
    tempbrojac = 0
    i = 0
    for broj in brojevi:
        listaImenaBrojeva.append(broj['name'])
        listaLinkovaBrojeva.append(broj['link'])
    
    #print("ListaLinkovaBrojeva", listaLinkovaBrojeva)
    while tempbrojac < len(listaLinkovaBrojeva):
        for link in listaLinkovaBrojeva:       
            temp.append(downloadHrArchive(listaLinkovaBrojeva[tempbrojac]))
            tempbrojac += 1
        nBrojeva = len(temp)
        tupleClanakaUBroju = []
        for i in range(0, nBrojeva):
            broj = temp[i]
            #print("\n\nBROJ: \n\n", broj) #broj je lista imelink KVova
            for tupla in broj:
                if tupla['name'] not in ["Sadržaj", ""]:
                    spl = tupla['link'].split("/")
                    if 'index.php' in spl[3]:
                        file.write(tupla['link'])
                        file.write("\n")
          
    file.close()
    print("Text file s popison HR linkova napravljen.")

def createHtmlURLtxtENG(casopisLink):
    brojevi = downloadInfo(casopisLink)
    file = open("HTMLlinkoviENG.txt", "w")
    listaImenaBrojeva = []    
    listaLinkovaBrojeva = []
    temp = []
    tempbrojac = 0
    i = 0
    for broj in brojevi:
        listaImenaBrojeva.append(broj['name'])
        listaLinkovaBrojeva.append(broj['link'])
    
    #print("ListaLinkovaBrojeva", listaLinkovaBrojeva)
    while tempbrojac < len(listaLinkovaBrojeva):
        for link in listaLinkovaBrojeva:       
            temp.append(downloadEngArchive(listaLinkovaBrojeva[tempbrojac]))
            tempbrojac += 1
        nBrojeva = len(temp)
        tupleClanakaUBroju = []
        for i in range(0, nBrojeva):
            broj = temp[i]
            print("\n\nBROJ: \n\n", broj) #broj je lista imelink KVova
            for tupla in broj:
                if tupla['name'] not in ["Sadržaj", ""]:
                    spl = tupla['link'].split("/")
                    if 'index.php' in spl[3]:
                        file.write(tupla['link'])
                        file.write("\n")
          
    file.close()
    print("Text file s popison ENG linkova napravljen.")


# =============================================================================
# Funkcija za dohvatanje autora članka i naslova, staviti rezultat u listu
# od dva elementa, to će kasnije ići u fajl.
# =============================================================================
def getAutorAndNaslov(link):
    r = requests.get(link)
    source = r.text.encode(r.encoding)
    soup = BeautifulSoup(source, features="lxml")
    autor = soup.find('meta', attrs={"name": "citation_author"})
    autor = autor.attrs["content"] + " - "
    naslov = soup.title.get_text()
    autNaslovPar = []
    autNaslovPar.append(autor)
    autNaslovPar.append(naslov)
    print("Autor i naslov dohvaćeni.")
    print("Naslov: ", autNaslovPar[1])
    return autNaslovPar
    

# =============================================================================
# Hvatamo ključne riječi članka, ispišu se kao string, odvojene novim redom.
# Druga funkcija hvata sažetak, njen rezultat je blok teksta (isto string).
# =============================================================================
def downloadKeywords(link):
    r = requests.get(link)
    source = r.text.encode(r.encoding)
    soup = BeautifulSoup(source, features="lxml")
    foo = soup.find_all('p')
    bar = foo[5].get_text().split(";")
    
    keywords = []
    for i in range(len(bar)):
        bar[i] = bar[i].replace("\t", " ")
        keywords.append(bar[i])
    keywords[0] = keywords[0][15:]
    
    kwds = ""
    for i in range(len(keywords)):
        kwds = kwds + "\n" + keywords[i]
    rezultat = "\nKljučne riječi: \n" + kwds + "\n"
    if len(rezultat) < 30:
        print("Članak nema ključne riječi!")
    else:
        print("Ključne riječi ovog članka dohvaćene.")
        return rezultat
    

def downloadAbstract(link):
    r = requests.get(link)
    source = r.text.encode(r.encoding)
    soup = BeautifulSoup(source, features="lxml")
    foo = soup.find_all('p')
    bar = foo[4].get_text()
    
    prvaRijec = bar[0:7]
    sazetak = "\nSažetak:\n" + bar.replace(prvaRijec, "")
    if len(sazetak) < 10:
        print("Sažetak ovog članka nije skinut, nema ga.")
    else:
        print("Sažetak ovog članka je skinut.")
        return sazetak

# =============================================================================
# Funkcija stvara txt fajl čiji se naslov sastoji od imena autora i imena
# članka, a u njoj su ispisane ključne riječi te sažetak. 
# Jedna je za hrvatske, druga za eng/ostale, glede lakše potencijalne 
# kategorizacije u folderu.
# Iterativno čita linkove iz HTMLlinkovi fajla, te radi pauzu od sekunde 
# nakon svakog poziva funkcije kako ne bi preplavila server.
# FUNKCIJA NE STVARA FAJL AKO NA TOM LINKU NEMA SAZETKA NI KLJUCNIH RIJECI.
# =============================================================================
def createTxtsForMagazine(txtfile):
    file = open(txtfile, "r")
    for link in file:
        try:
            
            link = link.replace("\n", "")
            autorInaslov = getAutorAndNaslov(link) #bolje pozvati samo jednom nego dvaput, optimizacija :)
            autor = autorInaslov[0]
            naslov = autorInaslov[1]
            time.sleep(2)
            keywords = downloadKeywords(link)
            time.sleep(2)
            sazetak = downloadAbstract(link)
            time.sleep(2)
            if naslov == "Sadržaj:":
                continue
            
            if naslov[-1] == ".":
                naslov = naslov.replace(".", "")
            
            if ":" in naslov:
                naslov = naslov.replace(":", "")
            
            if len(keywords) < 40:
                print("Ovo u sebi nema kljucne rijeci (", len(keywords), " znakova), ne stvaram fajl ", naslov ,".")
                continue
            
            if len(sazetak) < 40:
                print("Ovo u sebi nema sazetak (", len(sazetak), " znakova), ne stvaram fajl ", naslov ,".")
                continue
            
            filename = autor + naslov + ".txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(naslov)
                f.write(keywords)
                f.write(sazetak)
            f.close()
            print("Fajl stvoren!\n\n")
            time.sleep(2)
        except AttributeError:
            #print(AttributeError.__traceback__)
            print("Nevazeci fajl, idemo dalje.")
            #pass
    file.close()



# =============================================================================
# U prve funkcije samo ubaciti link na časopis i program radi svoje.
# =============================================================================
def main():
    createHtmlURLtxtENG("https://hrcak.srce.hr/kroatologija")
    createHtmlURLtxtHR("https://hrcak.srce.hr/kroatologija")
    
    createTxtsForMagazine("HTMLlinkoviENG.txt")
    createTxtsForMagazine("HTMLlinkoviHR.txt")
    
    


if __name__ == "__main__":
    main()
    