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
import os
import fitz

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
#   
# DownloadPDFArchive vraća listu discotva koji su naslov pdfa i link pdfa.
# =============================================================================
def downloadPdfArchive(link):
    archivePdf = []
    nl = {}
    c = urlopen(link).read()
    s = BeautifulSoup(c, features="lxml")
    parent = s.find_all('td', 'al-r no-wrap')
    hrefHr = s.find_all('a') 
    for a in hrefHr:
        if a.parent in parent:
            nl["name"] = a['title']
            nl["link"] = "https://hrcak.srce.hr" + a['href']
            #print("name:", nl["name"], "\nlink:", nl["link"])
            archivePdf.append(nl)
            
    print("ArchivePdf:", archivePdf)
    return archivePdf
    
# =============================================================================
# def downloadPdfArchive(link): LAST WORKING VERSION
#    archivePdf = []
#    c = urlopen(link).read()
#    s = BeautifulSoup(c, features="lxml")
#    parent = s.find_all('td', 'al-r no-wrap')
#    hrefHr = s.find_all('a')
#    for a in hrefHr:
#        if a.parent in parent:
#            link = "https://hrcak.srce.hr" + a['href']
#            archivePdf.append(link)
#    
#    print("ArchivePdf:", archivePdf)
#    return archivePdf
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
    #print("ARCHIVE HR: ", archiveHr)
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
    
    print("ARCHIVE ENG: ", archiveEng)
    print("Download liste engleskih članaka gotov za ovaj broj.")
    return archiveEng


# =============================================================================
# Ovo u mainu pokrecemo prvo, zadavsi mu link na casopis. Izvadit ce linkove
# ka hrvatskom jeziku. Note: u fajl zapisuje i znak za newline, kojeg cemo 
# kasnije morati replaceati. Nakon nje je funkcija za isto, ali na 
# ostalim jezicima.
# Nema veze što nije svaki članak u ENG na engleskom, jer ćemo u kasnijim
# funkcijama skippati htmlice koje u sebi nemaju 'Sažetak' ili w/ever.
#    
#   PRVO HR, PA ENG, jer usput obje popune Naslov id txt koji ce nam trebat
#   za spajanje tekstove iz pdf fajlova sa HTMLtxticama 
# =============================================================================

    
def createHtmlURLtxtHR(casopisLink):
    brojevi = downloadInfo(casopisLink)
    file = open("HTMLlinkoviHR.txt", "w")
    pdfidstitles = open("Naslov id.txt", "w", encoding = "utf-8")
    listaImenaBrojeva = []    
    listaLinkovaBrojeva = []
    temp = []
    tempbrojac = 0
    i = 0
    for broj in brojevi:
        listaImenaBrojeva.append(broj['name'])
        listaLinkovaBrojeva.append(broj['link'])
    while tempbrojac < len(listaLinkovaBrojeva):
        for link in listaLinkovaBrojeva:       
            temp.append(downloadHrArchive(listaLinkovaBrojeva[tempbrojac]))
            tempbrojac += 1
        #print("temp: ", temp)
        nBrojeva = len(temp)
        tupleClanakaUBroju = []
        for i in range(0, nBrojeva):
            broj = temp[i]
            #print("\n\nBROJ: \n\n", broj)
            for tupla in broj:
                if tupla['name'] not in ["Sadržaj", ""]:
                    spl = tupla['link'].split("/")
                    iD = tupla['link'].split("=")[-1]                
                    naslov = tupla["name"]         
                    line = iD + " " + naslov + "\n"
                    file.write(tupla['link'] + "\n")                   
                    pdfidstitles.write(line)
    file.close()
    pdfidstitles.close()
    print("Text file s popison HR linkova napravljen.")

def createHtmlURLtxtENG(casopisLink):
    brojevi = downloadInfo(casopisLink)
    file = open("HTMLlinkoviENG.txt", "w")
    pdfidstitles = open("Naslov id.txt", "a", encoding = "utf-8")
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
            #print("\n\nBROJ: \n\n", broj) #broj je lista imelink KVova
            for tupla in broj:
                if tupla['name'] not in ["Sadržaj", ""]:
                    spl = tupla['link'].split("/")
                    iD = tupla['link'].split("=")[-1]                
                    naslov = tupla["name"]         
                    line = iD + " " + naslov + "\n"
                    file.write(tupla['link'] + "\n")                   
                    pdfidstitles.write(line)
    pdfidstitles.close()
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
    #print("Naslov: ", autNaslovPar[1])
    return autNaslovPar
    

# =============================================================================

# =============================================================================

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
    file = open(txtfile, "r", encoding="UTF-8")
    check = open("Naslov id.txt", "r", encoding="UTF-8")
    for link in file:
        try:
            
            link = link.replace("\n", "")
            try:
                autorInaslov = getAutorAndNaslov(link) #bolje pozvati samo jednom nego dvaput, optimizacija :)
                autor = autorInaslov[0]
                naslov = autorInaslov[1]
            except ConnectionError:
                print("Pukla veza")
                continue
            
            for dupl in check:
                #print("dupl:", dupl)
                implore = re.split('[^a-zA-Z]', dupl)
                #print("Implore", implore)
            
                ajdi = dupl.split(" ")[0]
                #print(ajdi)
                pdf = ajdi + ".pdf"
                if os.path.exists(pdf):
                    pdftext = getPDFText(pdf)
                    if implore[7] in pdftext:
                        print(pdftext)
                    
                
            if naslov == "Sadržaj:":
                continue
            
            if naslov[-1] == ".":
                naslov = naslov.replace(".", "")
            
            if ":" in naslov:
                naslov = naslov.replace(":", "")
                
            if "\"" in naslov:
                naslov = naslov.replace("\"", "'")
            
            
            filename = ajdi + ".txt"
            
            if filename[:-4] == ajdi:
                pdftext = getPDFText(pdf)
                print(pdftext)
            
            
            if os.path.exists(filename):
                print("Članak ", filename, "već postoji, preskačem.")
                continue
            #print("PDFids:", pdfIds)
            time.sleep(2)
            
            try:
                keywords = downloadKeywords(link)
                if len(keywords) < 40:
                    print("Ovo u sebi nema kljucne rijeci (", len(keywords), " znakova), ne stvaram fajl ", naslov ,".")
                    continue
            except TypeError:
                print("Ovo nema keywordove, idemo dalje.")
                continue
            
            time.sleep(2)
            
            sazetak = downloadAbstract(link)
            if len(sazetak) < 40:
                print("Ovo u sebi nema sazetak (", len(sazetak), " znakova), ne stvaram fajl ", naslov ,".")
                continue
            time.sleep(2)
            
            
            with open(filename, 'w', encoding='utf-8') as f: 
                f.write(naslov)
                f.write(keywords)
                f.write(sazetak)
                #f.write(pdftext)
                if filename in pdftext:
                    for i in len(pdftext):
                        f.write(i)

                
            f.close()
            print("Fajl stvoren!\n\n")
            time.sleep(2)
        except AttributeError:
            #print(AttributeError.__traceback__)
            print("Nevazeci fajl, idemo dalje.")
            #pass
    
    file.close()


# =============================================================================
# Funkcija za stvaranje fajla s popisom linkova na PDFove. 
# Također vraća listu imena pdfova.
# =============================================================================

def createPDFurlTXT(casopisLink):
    brojevi = downloadInfo(casopisLink)
    file = open("PDFoviLinkovi.txt", "w")
    listaImenaBrojeva = []    
    listaLinkovaBrojeva = []
    temp = []
    temp2 = []
    tempbrojac = 0
    i = 0
    for broj in brojevi:
        listaImenaBrojeva.append(broj['name'])
        listaLinkovaBrojeva.append(broj['link'])
    
    
    #print("ListaLinkovaBrojeva", listaLinkovaBrojeva)
    #print("ListaImenaBrojeva", listaImenaBrojeva)
    while tempbrojac < len(listaLinkovaBrojeva):
        for link in listaLinkovaBrojeva:       
            temp.append(downloadPdfArchive(listaLinkovaBrojeva[tempbrojac])["link"])
            temp2.append(downloadPdfArchive(listaLinkovaBrojeva[tempbrojac])["name"])
            time.sleep(2)
            tempbrojac += 1
    #TEMP izbaci listu koja sadrži nekoliko listi, svaka od tih sadrži linkove 
    #na pdfove tog broja u časopisu
    print("temp:", temp)
    print("temp2", temp)
#    listaImenaPdfova = []
#    for i in temp:
#        for j in i:
#            #print("j: ", j)
#            ime = j.split("/")[-1]
#            listaImenaPdfova.append(ime)
#            file.write(j + "\n")
#    #print(listaImenaPdfova)
#    file.close()
#    ids = open("PDFids.txt", "w")
#    for ime in listaImenaPdfova:
#        ids.write(ime + "\n")
#    ids.close()
#    print("Txt s linkovima na PDFove napravljen")
#    


    
# =============================================================================
# Funkcija za skidanje PDFova iz PDFoviLinkovi.txt iterativno.
# =============================================================================

def downloadPdfs(file):
      file = open(file, "r")
      
      for link in file:
          link = link.replace("\n", "")
          path = link.split("/")[-1]
          url = link
          print("path:", path)
          print("url:", url)
          r = requests.get(url, stream=True)
          if r.status_code == 200:
              with open(path + ".pdf", 'wb') as f:
                  for chunk in r:
                      f.write(chunk)
              
      file.close()
        


# =============================================================================
# Funkcija vadi tekst iz .pdf filea. Returna listu u kojoj je svaki element tekst
# s pojedine stranice.
# =============================================================================
def getPDFText(file):
   doc = fitz.open(file)
   pages = []
   for page in range (0, doc.pageCount):
       loaded = doc.loadPage(page)
       text = loaded.getText()
       pages.append(text)
   return pages
  

# =============================================================================
# U prve funkcije samo ubaciti link na časopis i program radi svoje.
# U slučaju da server ne responda zbog nekog ConnectionErrora ili slično, ta se   
# iteracija preskače, jedan članak više-manje... Treba nam samo što veći dataset.
# =============================================================================
def main(): 
    
    #createHtmlURLtxtHR("https://hrcak.srce.hr/kroatologija")
    #createTxtsForMagazine("HTMLlinkoviHR.txt")
    #createHtmlURLtxtHR("https://hrcak.srce.hr/kroatologija")
    #createHtmlURLtxtENG("https://hrcak.srce.hr/kroatologija")
    #downloadPdfArchive("https://hrcak.srce.hr/index.php?show=toc&id_broj=17922")
    #listaIdjevaBrojeva = createPDFurlTXT("https://hrcak.srce.hr/kroatologija")
    #downloadPdfs("PDFoviLinkovi.txt")
    #getPDFText("300740.pdf")
    #createTxtsForMagazine("HTMLlinkoviHR.txt", listaIdjevaBrojeva)
    #createTxtsForMagazine("HTMLlinkoviHR.txt")
    #downloadPdfArchive("https://hrcak.srce.hr/index.php?show=toc&id_broj=17922")
    createPDFurlTXT("https://hrcak.srce.hr/kroatologija")
if __name__ == "__main__":
    main()



# =============================================================================
# FUNKCIJE ZA KASNIJE:
    
    
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
    
  def getPdfKeywords(pdf):
  doc = fitz.open(pdf)
  page1 = doc.loadPage(1) #fitz open van funkcije pa stavit nek iterativno idu brojevi stranice
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
  print(klj)
  #truKlj = klj.split("Keywords:")
  #print(truKlj) #ovo je sad lista s dva elementa, prvi su kljucne rijeci, drugi 
  #su keywords
    
  
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
    print("getPdfAbstract done.")



  """
# =============================================================================

