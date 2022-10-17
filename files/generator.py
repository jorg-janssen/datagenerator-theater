
import json
import random
import datetime
import py2sql

AANTAL_BEDRIJVEN = 10   # minimaal 10
AANTAL_SCHEPEN = 3      # minimaal 3
AANTAL_VISSOORTEN = 10  # minimaal 10
AANTAL_LANDEN = 6       # minmiaal 6
AANTAL_VISTOCHTEN = 5   # minimaal 5

#vangstlanden = json.load(open('datafiles/vangstlanden.json', 'r'))
bron_landen = json.load(open('datafiles/licentielanden.json', 'r'))
bron_bedrijven = json.load(open('datafiles/bedrijven.json', 'r'))
bron_schepen = json.load(open('datafiles/schepen.json', 'r'))
vissoorten = json.load(open('datafiles/vissoorten.json', 'r'))

datums = [datetime.date(2016, 1, 1)]
while datums[-1] != datetime.date(2021, 12, 31):
    nieuw = datums[-1] + datetime.timedelta(days=1)
    datums.append(nieuw)

def __main__():

    file = open("inserts.sql", "w")
    file.write("SET NOCOUNT ON\ngo\n")   

    # maak landen
    landen = random.sample(bron_landen, k = AANTAL_LANDEN)

    # maak holdings, moederbedrijven en gewone bedrijven
    bedrijven = []
    holdings = random.sample(bron_bedrijven, k = int(AANTAL_BEDRIJVEN/10)) # maak 10% holdings
    for bedrijf in holdings:
        mydict = {}
        mydict["BEDRIJFSNAAM"] = bedrijf["bedrijfsnaam"]
        mydict["EIGENAAR"] = None
        bedrijven.append(mydict)
    moederbedrijven = random.sample(bron_bedrijven, k = int(AANTAL_BEDRIJVEN/5)) # maak 20% moederbedrijven 
    for bedrijf in moederbedrijven:
        if bedrijf not in holdings:
            mydict = {}
            mydict["BEDRIJFSNAAM"] = bedrijf["bedrijfsnaam"]
            mydict["EIGENAAR"] = random.choice(holdings)["bedrijfsnaam"]
            bedrijven.append(mydict)
    aantalbedrijven = 0                      # vul de rest van de bedrijven aan
    while aantalbedrijven < AANTAL_BEDRIJVEN:
        bedrijf = random.choice(bron_bedrijven)
        if(bedrijf not in holdings and bedrijf not in moederbedrijven):
            mydict = {}
            mydict["BEDRIJFSNAAM"] = bedrijf["bedrijfsnaam"]
            mydict["EIGENAAR"] = random.choice(moederbedrijven)["bedrijfsnaam"]
            bedrijven.append(mydict)
            aantalbedrijven += 1

    # koppel landen aan bedrijven
    for bedrijf in bedrijven:
        land = random.choice(landen)
        bedrijf["LANDNAAM"] = land["landnaam"] 
    
    # koppel schip aan willekeurig bedrijf (ook aan moederbedrijven maar niet aan holdings)
    schepen = random.sample(bron_schepen, k = AANTAL_SCHEPEN)
    for schip in schepen:        
        bedrijf = random.choice(bedrijven)
        while (bedrijf["EIGENAAR"] == None ): # holding?
            bedrijf = random.choice(bedrijven)        
        schip["BEDRIJFSNAAM"] = bedrijf["BEDRIJFSNAAM"]
    
    # genereer inserts basistabellen
    print ("LAND: ", py2sql.list2sql2file('LAND', landen, file))    
    print ("BEDRIJF: ", py2sql.list2sql2file('BEDRIJF', bedrijven, file))    
    print ("SCHIP: ", py2sql.list2sql2file('SCHIP', schepen, file)) 
    
    # plaats random factoren
    for land in landen:
        land["factor"] = 1 + random.random()*2
    for land in landen:
        land["factor"] = 1 + random.random() *2       
    for vissoort in vissoorten:
        vissoort["factor"] = 1 + random.random()*3
    for schip in schepen:
        schip["factor"] = 1 + random.random()*5  
        
    # genereer inserts overige tabellen
    genereer_scheepsvlaggen(file, schepen, landen)
    genereer_vangsten(file, schepen, landen) 
    genereer_vislicenties(file, schepen, landen)

    file.close()     
    
def genereer_vangsten(file, schepen, landen):
    
    vangsten = []

    for schip in random.sample(schepen, k = random.randrange(len(schepen)-3,len(schepen)-1)):  # bijna alle schepen

        for datum in random.sample(datums, k = AANTAL_VISTOCHTEN): # een aantal vistochten 
        
            # minder vangst in winter en meer in zomer = maandfactor
            maandfactor = datum.month-7
            if maandfactor >= 0:
                maandfactor += 1
            maandfactor = abs(maandfactor)*5
            jaarfactor = 1+(datum.year-2015)/10 # ieder jaar een beetje meer
 
            for land in random.sample(landen, k = random.randrange(1,3)): # een paar landen per vistocht
            
                for vis in random.sample(vissoorten, k = int(AANTAL_VISSOORTEN/10)): # 10% van de vissoorten
                
                    vangst = {}
                 
                    hoeveelheid = int(random.randrange(1,50)*schip["factor"]*jaarfactor*land["factor"]*vis["factor"]/maandfactor)
                    vangst["SCHEEPSNAAM"] = schip["scheepsnaam"]
                    vangst["LANDNAAM"] = land["landnaam"]
                    vangst["DATUM"] = datum.strftime('%Y-%m-%d')
                    vangst["VISSOORT_GEVANGEN"] = vis["vissoortnaam"]
                    vangst["HOEVEELHEID"] = str(hoeveelheid)
                    
                    vangsten.append(vangst)   
                    
              
    print ("VANGST: ", py2sql.list2sql2file('VANGST', vangsten, file))       


def genereer_vislicenties(file, schepen, landen):

    vislicenties = []

    for schip in random.sample(schepen, k = random.randrange(len(schepen)-3,len(schepen)-1)): # bijna alle schepen
            
            for land in random.sample(landen, k = random.randrange(2,len(landen)-2)): # veel landen
          
                for vis in random.sample(vissoorten, k = int(AANTAL_VISSOORTEN/2)):  # de helft van de vissoorten                 
          
                    begindatum = datetime.date(2016, 1, 1) - datetime.timedelta(days=random.randrange(0,3000)) # een paar wisselingen
                    einddatum = datetime.date(2016, 1, 1)
                    
                    while einddatum < datetime.date(2021, 12, 31):  

                        einddatum = begindatum + datetime.timedelta(days=random.randrange(300,5000))
                        
                        licentie = {}
                    
                        licentie["SCHEEPSNAAM"] = schip["scheepsnaam"]
                        licentie["LANDNAAM"] = land["landnaam"]
                        licentie["L_VANAF"] = begindatum.strftime('%Y-%m-%d')                        
                        licentie["VISSOORT_LICENTIE"] = vis["vissoortnaam"]                         

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
        
            vlag["SCHEEPSNAAM"] = schip["scheepsnaam"]
            vlag["LANDNAAM"] = land["landnaam"]    
            vlag["VLAG_VANAF"] = begindatum.strftime('%Y-%m-%d')       

            if einddatum >= datetime.date(2021, 12, 31): # data tot 2021-12-31
                vlag["VLAG_TM"] = None
            else:
                vlag["VLAG_TM"] = einddatum.strftime('%Y-%m-%d')  # en anders een nieuwe periode starten de dag erna
                begindatum = einddatum + datetime.timedelta(days=1)
            
            scheepsvlaggen.append(vlag)

    print ("SCHEEPSVLAG", py2sql.list2sql2file('SCHEEPSVLAG', scheepsvlaggen, file))      


__main__()

