
import json
import random
import datetime
import py2sql

zalen = []
rangen = []
klanten = []
voorstellingen = []
uitvoeringen = [] 
reserveringen = []
bezettingen = []
prijzen = []

voorstellingsnr = 1 
reserveringsnr = 1001   

data = []


         
def __main__():
    global voorstellingsnr
   
    # import files for some base tables
    zalen_bron = json.load(open('datafiles/zalen.json', 'r'))
    rangen.extend(json.load(open('datafiles/rangen.json', 'r')))
    voorstellingen_bron = json.load(open('datafiles/voorstellingen.json', 'r'))    
    print(len(voorstellingen_bron))
    
    # import helper files
    firstnames_bron = json.load(open('datafiles/firstnames.json', 'r'))
    lastnames_bron = json.load(open('datafiles/lastnames.json', 'r'))
    postcodes_bron = json.load(open('datafiles/postcodes.json', 'r'))
    #adressen = json.load(open('datafiles/adressen.json', 'r'))
    
    # generate helper lists   
    
    data.append(datetime.date(2018, 1, 1))
    while data[-1] != datetime.date(2022, 12, 31):
        new = data[-1] + datetime.timedelta(days=1)
        data.append(new)          

    #klanten
    for klantnr in range(1001, 11000):
        klant = {}
        klant["klantnummer"] = klantnr
        klant["achternaam"] = random.choice(lastnames_bron)
        klant["voorletter"] = random.choice(firstnames_bron)[0]
        klant["geslacht"] = random.choice(["M","V", None])
        postcode_en_city = random.choice(postcodes_bron)
        klant["postcode"] = postcode_en_city["postcode"]
        klant["woonplaats"] = postcode_en_city["city"]
        klanten.append(klant) 

    # per zaal
    for zaal in zalen_bron:
        zalen.append(zaal)
        # voorstellingen
        dagen_gebruikt = 0
        while dagen_gebruikt < 4 * 365 and len(voorstellingen_bron) > voorstellingsnr:            
            voorstelling = voorstellingen_bron[voorstellingsnr]            
            voorstelling["voorstellingsnummer"] = voorstellingsnr + 100000
            if "titel" not in voorstelling: 
                voorstelling["titel"] = "Onbekende titel"
            if "genre" not in voorstelling:
                voorstelling["genre"] = None
            voorstellingen.append(voorstelling)
            duur = random.choice([45, 60, 90, 120, 135, 150])  
            datum = data[dagen_gebruikt]
            datum = datetime.datetime.combine(datum, datetime.datetime.min.time())
            populariteitsfactor = random.randint(1,10)
            # prijzen
            for rang in rangen:
                if rang["zaalnummer"] == zaal["zaalnummer"]:
                    prijs = {}
                    prijs["voorstellingsnummer"] = voorstelling["voorstellingsnummer"]
                    prijs["zaalnummer"] = zaal["zaalnummer"]
                    prijs["rangnummer"] = rang["rangnummer"]
                    prijs["prijs"] = (populariteitsfactor * random.randint(5, 25)) / (rang["rangnummer"] * random.randint(75,125)/100)
                    prijzen.append(prijs)
            # uitvoeringen
            aantal_uitvoeringen = random.randint(1,6)  # 1 tot 6 uitvoeringen per voorstelling
            uitvoeringsnr = 0
            while uitvoeringsnr <= aantal_uitvoeringen:
                uitvoeringsnr = uitvoeringsnr + 1  
                beginuur = random.randint(19,21)
                beginminuut = random.choice([0,30])              
                uitvoering = maak_uitvoering(voorstelling, uitvoeringsnr, zaal, datum, beginuur, beginminuut, duur, populariteitsfactor)
                uitvoeringen.append(uitvoering)
                #matinee-uitvoering
                if random.randint(0,10) < 2:
                    uitvoeringsnr = uitvoeringsnr + 1    
                    beginuur = random.randint(14,16)
                    beginminuut = random.choice([0,30])                                       
                    uitvoering = maak_uitvoering(voorstelling, uitvoeringsnr, zaal, datum, beginuur, beginminuut, duur, int(populariteitsfactor/random.randint(1,3)))
                    uitvoeringen.append(uitvoering)
                dagen_tot_volgende_uitvoering =  random.randint(1,2) # volgende uitvoering een paar dagen later
                datum = datum + datetime.timedelta(days = dagen_tot_volgende_uitvoering)
                dagen_gebruikt = dagen_gebruikt + dagen_tot_volgende_uitvoering
            # naar volgende voorstelling:
            voorstellingsnr = voorstellingsnr + 1
            dagen_gebruikt = dagen_gebruikt + random.randint(1,4) # volgende voorstelling een paar dagen later  
        

    print("Writing file...")
    file = open("inserts.sql", "w")
    file.write("SET NOCOUNT ON\ngo\n")     

    py2sql.list2sql("Zaal", zalen, file)
    py2sql.list2sql("Rang", rangen, file)
    py2sql.list2sql("Klant", klanten, file)
    py2sql.list2sql("Voorstelling", voorstellingen, file)
    py2sql.list2sql("Uitvoering", uitvoeringen, file) 
    py2sql.list2sql("Reservering", reserveringen, file)
    py2sql.list2sql("Bezetting", bezettingen, file)
    py2sql.list2sql("Prijzen", prijzen, file)    


    file.close()

def maak_uitvoering(voorstelling, uitvoeringsnr, zaal, datum, beginuur, beginminuut, duur, populariteitsfactor):
    global reserveringsnr
    # avonduitvoering:
    uitvoering = {}
    uitvoering["voorstellingsnummer"] = voorstelling["voorstellingsnummer"] 
    uitvoering["uitvoeringsnummer"] = uitvoeringsnr  
    uitvoering["begindatumtijd"] = datum
    uitvoering["begindatumtijd"] =  uitvoering["begindatumtijd"] + datetime.timedelta(hours = beginuur)
    uitvoering["begindatumtijd"] =  uitvoering["begindatumtijd"] + datetime.timedelta(minutes = beginminuut)                            
    uitvoering["einddatumtijd"] = uitvoering["begindatumtijd"]  + datetime.timedelta(minutes = duur)
    uitvoering["zaalnummer"] = zaal["zaalnummer"]
    # voorbereiden reserveringen en bezetting:
    print(zaal["zaalnummer"])
    #rangen
    for rang in rangen:      
        if rang["zaalnummer"] == zaal["zaalnummer"]:
            stoelnr = rang["vanstoel"]
            # reserveringen    
            while stoelnr <= rang["totstoel"] - 8:
                reservering = {}
                reserveringsnr = reserveringsnr + 1
                reservering["reserveringsnummer"] = reserveringsnr
                reservering["klantnummer"] = random.choice(klanten)["klantnummer"]
                reservering["voorstellingsnummer"] = uitvoering["voorstellingsnummer"]
                reservering["uitvoeringsnummer"] = uitvoering["uitvoeringsnummer"]
                reserveringen.append(reservering)
                aantal_stoelen = random.randint(1,8) # 1 tot 8 stoeltjes per reservering        
                # bezetting
                for b in range(1, aantal_stoelen): 
                    bezetting = {}
                    bezetting["reserveringsnummer"] = reservering["reserveringsnummer"]
                    bezetting["stoelnummer"] = stoelnr
                    bezetting["voorstellingsnummer"] = reservering["voorstellingsnummer"]
                    bezetting["uitvoeringsnummer"] = reservering["uitvoeringsnummer"]
                    bezettingen.append(bezetting)  
                    stoelnr = stoelnr + 1
                stoelnr = stoelnr + random.randint(0, abs(populariteitsfactor-11)) # hier en daar wat lege stoeltjes 
    return uitvoering
    
def dicts2list(listOfDicts, item):
    list = []
    for dict in listOfDicts:
        list.append(dict[item])
    return list
    
def getConsonants(string):
  return ''.join([each for each in string if each not in "aeiouAEIOU"])
  
def checkPeriodOverlap(begindate1, enddate1, begindate2, enddate2):
    #print (begindate1, enddate1, begindate2, enddate2);
    result = False
    if date_in(begindate1, begindate2, enddate2):
        result =  True
    elif date_in(enddate1, begindate2, enddate2):
        result =  True
    elif date_in(begindate2, begindate1, enddate1):
        result =  True
    elif date_in(enddate2, begindate1, enddate1):
        result =  True
    elif enddate2 == None and enddate1 >= begindate2:
        result =  True
    elif enddate1 == None and begindate1 <= enddate2:
        result =  True
    #print(result)
    return result

def date_in(thedate, begindate, enddate):
    if thedate == None:
        return False
    elif begindate == None or thedate >= begindate: 
        if enddate == None or thedate <= enddate:
            return True
        else:
            return False
    else:
        return False

def tupels2dicts(name, listOfTupels):
    list = []
    for tupel in listOfTupels:
        mydict = {name: tupel}
        list.append(mydict)
    return list

__main__()

