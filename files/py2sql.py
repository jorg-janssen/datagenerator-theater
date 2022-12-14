import datetime

def list2sql(name, list, file):

    counter = 0      
    file.write("\nPRINT('Inserting in table " + name + "')\ngo\n")  
    
    if len(list) > 0:

        columns = list[0].keys()
    
        for item in list:
        
            if (counter % 1000 == 0):
                file.write("INSERT INTO " + name + " (" + ", ".join(columns) + ") VALUES \n  ")
            if (counter % 1000 != 0):
                file.write(",\n  ")
                
            file.write(dict2sql(columns, item)) 
            
            counter+=1
            
            if (counter % 1000 == 0):
                file.write(";\ngo\n") 
        

        
    file.write(";\ngo\nPRINT('" + str(counter) + " records')\ngo\n")  
    file.write("PRINT('')")
    return counter    


def dict2sql(columns, dict):

    sql = "("
    for item in columns:
        if item in dict: # alleen als item uit eerste record ook wel in dit record zit
            sql += value2sql(dict[item])
            sql += ", "
    sql = sql[:-2]
    sql += (")")
    return sql
        
def value2sql(value):

    sql = ""
    if (isinstance(value, (int,))):
        sql += str(value)
    elif (isinstance(value, (float,))):
        sql += str(value)        
    elif (isinstance(value, (str, ))):
        value = value.replace("'", "''")
        value = value.replace("''''", "''")
        sql += "'" + value + "'"
    elif (isinstance(value, (datetime.date, ))):
        sql += "'" + str(value) + "'"        
    elif (isinstance(value, type(None))):    
        sql += "NULL"
    else:
        print( "datatype unknown: " + str(type(value)))
    return sql



def list2sql2file(name, list, file): 
    
    file.write("\nPRINT('Inserting in table " + name + "')\ngo\n")  
    
    counter = 0  


    for item in list:
    
        if (counter % 1000 == 0):
            file.write("INSERT INTO " + name + " VALUES \n  ")
        if (counter % 1000 != 0):
            file.write(",\n  ")
            
        file.write(dict2sql(name, item)) 
        
        counter+=1
        
        if (counter % 1000 == 0):
            file.write(";\ngo\n") 
        

        
    file.write(";\ngo\nPRINT('" + str(counter) + " records inserted')\ngo\n")  
    file.write("PRINT('')")
    return counter

