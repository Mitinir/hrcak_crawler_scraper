#!/bin/env python3

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse
from time import time as timer
import urllib.request
import re
import requests
import PyPDF2 as pdflib
import string
import wget
import os
import fitz
import shutil
import ntpath


"""
--------CRAWLY CRAWLY CRAWLER---------------
/*
/*
/*      KOLEGIJ: FORMALNI JEZICI I JEZIČNI PROFESORI
/*      AUTOR: IVAN BANOVIĆ
/*      
/*
---------SIJEČANJ 2019-----------------------
"""


"""
    TL;DR:
        Zadate programu URL časopisa kojeg treba procrawlati i 
        proscrapeati u varijablu INFO u mainu.
        On tada sa stranice tog časopisa izvuče jedan link na najnoviji 
        broj časopisa u dijelu stranice imena Arhiva.
        To radi funkcijom downloadInfo. 
        Pomoću downloadArchive dobijemo linkove na članke u tom broju časopisa.
        Linkovi na članke se sortiraju u dva fajla: jedan za linkove na pdf-ove, 
        drugi za linkove na članke u htmlu.
        
        U TEORIJI program iterativno za svaki link iz svake datoteke vadi ključne 
        riječi i sažetak te ih sprema svaki u svoju datoteku.
        
        PROBLEM: data mining iz pdfova je raketna znanost za sebe i ne postoji jedinstven
        alat koji može izvući tekst iz pdfa, koji su sami često autogenerirani bogznakakvim 
        softverom te određene firme ili stranice.
        
        
        to-do: 
        
            -funkcija koja stvara textove sa rezultatima, i to 
            named textove, za non-pdf fileove
        
            -funkcija koja stvara textove sa rezultatima, i to 
            named textove, za pdf fileove
            
            -def AutorGodinaNaziv
            
            -popraviti ono gdje ne čita linkove iz fajla kako bi trebalo, 
            mozda jer je sve binary?
        
            -multithreadanjem realizirati vadenje linkova?
            
            -downloadPdf funkcija nek se rijese permissioni za writeanje

"""

"""
Archives je isto resultset, izvadili smo sve a hrefove sa IDjem toc, jer je 
html takav kakav jest. header je isto bs4element.Tag
"""

#možda listom, umjesto dictom? Onda ne bi bile byte vrijednosti?
def downloadArchive(archivePage):
  archive = []
  c = urlopen(archivePage).read()
  s = BeautifulSoup(c, features="lxml")
  archives = s.find_all('a', 'toc') 
  
  for a in archives:
    it = {}
    header = a.parent.parent
    it['name'] = a.text.replace('\r\n', ' ').strip()
    it['link'] = 'https://hrcak.srce.hr' + header.find_all('a')[-1:][0]['href']
    
    archive.append(it)
  return archive

"""
Ova funkcija skida stranicu časopisa te
table i href su tipa bs4.element.Tag i bs4.element.ResultSet
i iz tog resultseta stvaramo dict sa key:valueovima name:link,
a pošto je name dosta tabban i ruzan, pomocu regexa (stackoverflow) ureden
da bude u normalnom formatu.
"""
#možda listom, umjesto dictom? Onda ne bi bile byte vrijednosti?
def downloadInfo(of):
    result = []
    c = urlopen(of).read()
    s = BeautifulSoup(c, features="lxml")
    table = s.find_all('table')[-1:][0]
    #print("Table: \n\n")
    #print(type(table))
    hrefs = table.find_all('a')
    #print("hrefs:\n\n")
    #print(type(hrefs))
    for it in hrefs:
        r = {}       
        r['link'] = 'https://hrcak.srce.hr' + it['href']
        r['name'] = list(it.children)[1].text
        #print(r['name'])
        r['name'] = re.sub(r"\s+", ' ', r['name'], flags=re.UNICODE).strip()       
        #print(r['name'])
        result.append(r)
        return result



"""
Funkcija vadi sažetak ili abstract iz html članka.
Ispalo je da je paragraf u kojem je sazetak 4i paragraf po redu, pa smo iz njega 
izvukli text pomoću get_text().
"""

def downloadNonPdfAbstract(nonPdfLink):
    r = requests.get(nonPdfLink)
    source = r.text.encode(r.encoding)
    soup = BeautifulSoup(source, features="lxml")
    saz = soup.find_all('p')
    #print(saz[4])
    sazetak = saz[4].get_text()
    print(sazetak)
    
"""

Ovdje je ispalo da su kljucne rijeci u petom <p>aragrafu, pa smo iz njega izvukli text
i splittali ga jer je bio odvojen semicolonima.
u iteratoru-- za svaki keyword u listi ide brisati tab na par nacina za svaki slucaj, 
te rezutate stavi u listu kys. Prvi element u listi jos uvijek ima "kljucne rijeci" u sebi 
pa smo ga zamijenili sa istim time, samo sto pocinje 15 charactera kasnije.
Onda printamo svaku kljucnu rijec u rasponu broja elemenata liste, iliti rasponu broja kljucnih rijeci.
"""
def downloadNonPdfKeywords(nonPdfLink): 
    #zašto radi samo na testlinku, a ne za svaki link u fajlu?
    r = requests.get(nonPdfLink)
    source = r.text.encode(r.encoding)
    soup = BeautifulSoup(source, features="lxml")
    saz = soup.find_all('p')
    
    keywords = saz[5].get_text().split(";")
    print(keywords)
    kys = []
    for i in range(len(keywords)):
        keywords[i] = re.sub(r"[\t]*", "", keywords[i])
        keywords[i] = re.sub(r"[\t]*", "", keywords[i])
        keywords[i].replace("\t", " ")
        #print(keywords[i])
        kys.append(keywords[i])
    #print(kys)
    kys[0] = kys[0][15:]
    #print(kys[0][15:])
    #print(kys)
    for i in range(len(kys)):
        print(kys[i])
        

#def getAutorGodinaNaziv(link)

"""
ZAŠTO NE ŽELI SEJVAT U FOLDER AAAAAA.
"""
def downloadPdf(link):
      path, url = link
      
      #path = ntpath.basename("") + 
      #if not os.path.exists(directory):
      
      r = requests.get(url, stream=True)
      if r.status_code == 200:
          with open(path, 'wb') as f:
            for chunk in r:
                f.write(chunk)

"""
Trenutno radi smao za testni fajl i sa manual unosom stranice na kojoj su keywordsi
stavljanjem broja u varijablu page1text.
APSTRAHIRATI DA VRIJEDI ZA BILO KOJI FAJL.
"""
def getPdfKeywords(pdf):
    
  doc = fitz.open(pdf)
  page1 = doc.loadPage(14) #manually dodati ovo zasad :()
  page1text = page1.getText("text")
  print(page1text) # to je string, iz njega treba nac podstring Keywords
  search1 = "Keywords:"
  search2 = "Ključne riječi:"
  if search1 in page1text:
      print("Keywords nadeno!")
      if search2 in page1text:
          print("Kljucne nadeno!")
  else:
      print("Nema!")
  rijeci = page1text.split("Ključne riječi:")
  #print(rijeci)   
  print("\n")
  #print(rijeci[-1])
  klj = rijeci[-1]
  #print(type(klj))
  klj.split("\n")
  #print(klj)
  truKlj = klj.split("Keywords:")
  #print(truKlj) #ovo je sad lista s dva elementa, prvi su kljucne rijeci, drugi 
  #su keywords
  kljucne = truKlj[0]
  keywords = truKlj[1]
  
  print(kljucne)
  print(keywords)




#test

def getPdfAbstract(pdf):
    doc = fitz.open(pdf)
    page1 = doc.loadPage(14) #manually dodati ovo zasad :()
    page1text = page1.getText("text")
    print(page1text) # to je string, iz njega treba nac podstring Keywords
    search1 = "Abstract"
    search2 = "Sažetak"
    if search1 in page1text:
        print("Abstract naden!")
        if search2 in page1text:
            print("Sazetak naden!")
    else:
        print("Nema!")
    sazetak = page1text.split("Ključne riječi:")
    print(sazetak[1])   
    print("\n")
    
  
"""
Dakle, varijabla info je lista. Iz te smo liste funkcijom 
downloadArchive i indeksima izvukli 
linkove na pojedinacne clanke tog broja casopisa. Ti su linkovi unutar liste i u key:value 
vrijednostima, gdje je ime key, a link value. Dakle sve su dictovi.
Iteratorom i prolazimo kroz svaki element liste (svaki dict) i iz njega vadimo link.
Taj link "pročistimo" i gledamo je li isti vodi na pdf, ili na html, jer su različite strukture.
Svaki ide u svoj .txt fajl koji se potom zatvara.
"""
def main():
  
  info = downloadInfo("https://hrcak.srce.hr/rasprave-ihjj") #IME ČASOPISA U NAVODNIKE
  
  #print(info)
  #print(downloadArchive(info[0]['link']))
  #print("\n\n\n\n")
  file1 = open("pdfLinkovi.txt", "wb")
  file2 = open("nonPdfLinkovi.txt", "wb")
  links = downloadArchive(info[0]['link'])
  
  #print(links)
  #print(type(links))
  #print(links)
  #print(len(links))
  for i in range(len(links)):
      cistiLink = links[i]['link'] + '\n'
      #print(cistiLink)
      #print(type(cistiLink))
      sp = cistiLink.split("/")
      #print(sp)
      if (sp[3] != 'file'):
          #print("hatemel", cistiLink)
          rez = cistiLink.encode("UTF-8")
          file2.write(rez)
          #file2.write(cistiLink)
      else:
          #print("pedeef", cistiLink)
          rez = cistiLink.encode("UTF-8")
          file1.write(rez)
          #file2.write(cistiLink)
  
  file1.close()
  file2.close()
    
  #Skidamo pdfove kroz linkove iz fajla i spremamo ih u radni direktorij.
  
  fajl = open('PdfLinkovi.txt')
  lUrlova = []
  for link in fajl:
        link = link.replace("\n", ".pdf")
        path = link.split("/")[-1].replace("\n",".pdf")
        tupl = (path, link)
        lUrlova.append(tupl)
  print(lUrlova)
  start = timer()
  
  for tupla in lUrlova:
         downloadPdf(tupla)
         
  """  
  #teoretski funkcija koja premjesti sve skinute pdfove u novi folder imena pdfovi
  #todo: popravi regex da stvara fajlove kako spada
  
  dir_path = 'Pdfovi'  
  for file in os.listdir():
      lst = []
      match = re.search(r'^[0-9]...[0-9]$', file)
      if match:
          lst.append(match)
      if not os.path.exists(dir_path):
          os.mkdir(dir_path)
      if os.path.exists(dir_path):
          for file in lst:
              print(file)
              shutil.move(file, dir_path)
  """   
  
      
  print(f"\nDownloadanje pdfova je trajalo:  {timer() - start}\n")
  print("Broj urlova: ", len(lUrlova))
  #print(listaPdfova) a list of nones
  print("Sadrzaji radnog foldera: \n", os.listdir()) 
  fajl.close()
  
  
  """
  VADIMO KEYWORDSE IZ ZADANOG PDFA
  """
  print("KLJUCNE RIJECI IZ PDFA: \n")
  testpedeef = "334013.pdf"
  getPdfKeywords(testpedeef)
  
  
  
  """
  VADIMO KEYWORDSE IZ ZADANE HTMLICE
  """
  print("\nKLJUCNE RIJECI S HTMLA: \n")
  testlink = "https://hrcak.srce.hr/index.php?show=clanak&id_clanak_jezik=334014"
  downloadNonPdfKeywords(testlink)
  
  """
  VADIMO ABSTRACT IZ ZADANE HTMLICE
  """
  print("\nSAZETAK IZ HTMLICE:\n")
  downloadNonPdfAbstract(testlink)
  
  """
  VADIMO ABSTRACT IZ ZADANOG PDFA
  """
  print("\nSAZETAK IZ PDFA:\n")
  getPdfAbstract(testpedeef)
  
if __name__=="__main__":
  main()
