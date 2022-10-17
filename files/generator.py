
import json
import random
import datetime
import py2sql

AANTAL_BEDRIJVEN = 40   # minimaal 10
AANTAL_SCHEPEN = 60      # minimaal 3
AANTAL_VISSOORTEN = 20  # minimaal 10
AANTAL_LANDEN = 8       # minmiaal 6
AANTAL_VISTOCHTEN = 5   # minimaal 5

bron_landen = json.load(open('datafiles/landen.json', 'r'))
bron_bedrijven = json.load(open('datafiles/bedrijven.json', 'r'))
bron_schepen = json.load(open('datafiles/schepen.json', 'r'))
bron_vissoorten = json.load(open('datafiles/vissoorten.json', 'r'))
bron_datums = [datetime.date(2016, 1, 1)]
while bron_datums[-1] != datetime.date(2021, 12, 31):
    nieuw = bron_datums[-1] + datetime.timedelta(days=1)
    bron_datums.append(nieuw)


def __main__():

    file = open("inserts.sql", "w")
    file.write("SET NOCOUNT ON\ngo\n")   

    # maak landen
    landen = tupels2dicts("LANDNAAM",random.sample(bron_landen, k = min(AANTAL_LANDEN, len(bron_landen))))

    # maak vissoorten
    vissoorten = tupels2dicts("VISSOORTNAAM", random.sample(bron_vissoorten, k = min(AANTAL_VISSOORTEN, len(bron_vissoorten))))

    # maak holdings, moederbedrijven en gewone bedrijven
    bedrijven = []
    holdings = random.sample(bron_bedrijven, k = int(AANTAL_BEDRIJVEN/10)) # maak 10% holdings
    for bedrijf in holdings:
        mydict = {}
        mydict["BEDRIJFSNAAM"] = bedrijf
        mydict["EIGENAAR"] = None
        bedrijven.append(mydict)
    moederbedrijven = random.sample(bron_bedrijven, k = int(AANTAL_BEDRIJVEN/5)) # maak 20% moederbedrijven 
    for bedrijf in moederbedrijven:
        if bedrijf not in holdings:
            mydict = {}
            mydict["BEDRIJFSNAAM"] = bedrijf
            mydict["EIGENAAR"] = random.choice(holdings)
            bedrijven.append(mydict)
    aantalbedrijven = len(holdings) + len(moederbedrijven)                      # vul de rest van de bedrijven aan
    for bedrijf in bron_bedrijven:
        if(bedrijf not in holdings and bedrijf not in moederbedrijven):
            mydict = {}
            mydict["BEDRIJFSNAAM"] = bedrijf
            mydict["EIGENAAR"] = random.choice(moederbedrijven)
            bedrijven.append(mydict)
            aantalbedrijven += 1
            if(aantalbedrijven == AANTAL_BEDRIJVEN): break
    # koppel landen aan bedrijven
    for bedrijf in bedrijven:
        land = random.choice(landen)
        bedrijf["LANDNAAM"] = land["LANDNAAM"] 
    
    # maak schepen 
    schepen = [] 
    for schip in random.sample(bron_schepen, k = min(AANTAL_SCHEPEN, len(bron_schepen))):           
        mydict = {}     
        mydict["SCHEEPSNAAM"] = schip
        bedrijf = random.choice(bedrijven) # koppel schip aan willekeurig bedrijf (ook aan moederbedrijven maar niet aan holdings)
        while (bedrijf["EIGENAAR"] == None ): # holding?
            bedrijf = random.choice(bedrijven)        
        mydict["BEDRIJFSNAAM"] = bedrijf["BEDRIJFSNAAM"]
        schepen.append(mydict)
    
    # genereer inserts basistabellen
    print ("LAND: ", py2sql.list2sql2file('LAND', landen, file))    
    print ("BEDRIJF: ", py2sql.list2sql2file('BEDRIJF', bedrijven, file))    
    print ("SCHIP: ", py2sql.list2sql2file('SCHIP', schepen, file)) 
    
    # plaats random factoren
    for land in landen:
        land["factor"] = 1 + random.random()*2
    for vissoort in vissoorten:
        vissoort["factor"] = 1 + random.random()*3
    for schip in schepen:
        schip["factor"] = 1 + random.random()*5  
        
    # genereer inserts overige tabellen
    genereer_vangsten(file, schepen, landen, vissoorten) 
    genereer_vislicenties(file, schepen, landen, vissoorten)
    genereer_scheepsvlaggen(file, schepen, landen)    

    file.close()     
    
def genereer_vangsten(file, schepen, landen, vissoorten):
    
    vangsten = []

    for schip in random.sample(schepen, k = random.randrange(len(schepen)-3,len(schepen)-1)):  # bijna alle schepen

        for datum in random.sample(bron_datums, k = AANTAL_VISTOCHTEN): # een aantal vistochten 
        
            # minder vangst in winter en meer in zomer = maandfactor
            maandfactor = datum.month-7
            if maandfactor >= 0:
                maandfactor += 1
            maandfactor = abs(maandfactor)*5
            jaarfactor = 1+(datum.year-2015)/10 # ieder jaar een beetje meer
 
            for land in random.sample(landen, k = random.randrange(3,6)): # een paar landen per vistocht
            
                for vis in random.sample(vissoorten, k = int(AANTAL_VISSOORTEN/10)): # 10% van de vissoorten
                
                    vangst = {}
                 
                    hoeveelheid = int(random.randrange(1,50)*schip["factor"]*jaarfactor*land["factor"]*vis["factor"]/maandfactor)
                    vangst["SCHEEPSNAAM"] = schip["SCHEEPSNAAM"]
                    vangst["LANDNAAM"] = land["LANDNAAM"]
                    vangst["DATUM"] = datum.strftime('%Y-%m-%d')
                    vangst["VISSOORT_GEVANGEN"] = vis["VISSOORTNAAM"]
                    vangst["HOEVEELHEID"] = hoeveelheid
                    
                    vangsten.append(vangst)   
                    
              
    print ("VANGST: ", py2sql.list2sql2file('VANGST', vangsten, file))       


def genereer_vislicenties(file, schepen, landen, vissoorten):

    vislicenties = []

    for schip in random.sample(schepen, k = random.randrange(len(schepen)-3,len(schepen)-1)): # bijna alle schepen
            
            for land in random.sample(landen, k = int(AANTAL_LANDEN/2)): # de helft van de landen
          
                for vis in random.sample(vissoorten, k = int(AANTAL_VISSOORTEN/2)):  # de helft van de vissoorten                 
          
                    begindatum = datetime.date(2016, 1, 1) - datetime.timedelta(days=random.randrange(0,1000)) # een paar wisselingen
                    einddatum = datetime.date(2016, 1, 1)
                    
                    while einddatum < datetime.date(2021, 12, 31):  

                        einddatum = begindatum + datetime.timedelta(days=random.randrange(300,5000)) # hoe korter de periode, hoe meer wisselingen en records
                        
                        licentie = {}
                    
                        licentie["SCHEEPSNAAM"] = schip["SCHEEPSNAAM"]
                        licentie["LANDNAAM"] = land["LANDNAAM"]
                        licentie["L_VANAF"] = begindatum.strftime('%Y-%m-%d')                        
                        licentie["VISSOORT_LICENTIE"] = vis["VISSOORTNAAM"]                         

                        if einddatum >= datetime.date(2021, 12, 31): # data tot 2021-12-31
                            licentie["L_TM"] = None
                        else:
                            licentie["L_TM"] = einddatum.strftime('%Y-%m-%d') # en anders een nieuwe periode starten de dag erna
                            begindatum = einddatum + datetime.timedelta(days=1)
                            
                        licentie["QUOTUM"] = int(random.randrange(50,500)*schip["factor"]*land["factor"]*vis["factor"]) 
                        
                        vislicenties.append(licentie)
                        
    print ("VISLICENTIE", py2sql.list2sql2file('VISLICENTIE', vislicenties, file))    

def genereer_scheepsvlaggen(file, schepen, landen):

    scheepsvlaggen = []

    for schip in schepen:

        begindatum = datetime.date(2016, 1, 1) - datetime.timedelta(days=random.randrange(0,3000)) # een paar wisselingen
        einddatum = datetime.date(2016, 1, 1)
        
        while einddatum < datetime.date(2021, 12, 31):  
            land = random.choice(landen)
            einddatum = begindatum + datetime.timedelta(days=random.randrange(300,5000))
            
            vlag = {}
        
            vlag["SCHEEPSNAAM"] = schip["SCHEEPSNAAM"]
            vlag["LANDNAAM"] = land["LANDNAAM"]    
            vlag["VLAG_VANAF"] = begindatum.strftime('%Y-%m-%d')       

            if einddatum >= datetime.date(2021, 12, 31): # data tot 2021-12-31
                vlag["VLAG_TM"] = None
            else:
                vlag["VLAG_TM"] = einddatum.strftime('%Y-%m-%d')  # en anders een nieuwe periode starten de dag erna
                begindatum = einddatum + datetime.timedelta(days=1)
            
            scheepsvlaggen.append(vlag)

    print ("SCHEEPSVLAG", py2sql.list2sql2file('SCHEEPSVLAG', scheepsvlaggen, file))      

def tupels2dicts(name, listOfTupels):
    list = []
    for tupel in listOfTupels:
        mydict = {name: tupel}
        list.append(mydict)
    return list

__main__()

