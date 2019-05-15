import pymysql
import xmlrpc.client

#Configuration
url = 'http://8d5e81e1.ngrok.io'
db = 'Bodegas_Barylak'
username = 'bodegasbarylak1@gmail.com'
password = 'seacercalavendimia'


#Logging in
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
print(common.version())
uid = common.authenticate(db, username, password, {})


#Calling methods
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

print('Calling methods\n -------------------------\n')
print(models.execute_kw(db, uid, password,
    'res.partner', 'check_access_rights',
    ['read'], {'raise_exception': False}))
print('\n-------------------------')

#List records
print('List records\n -------------------------\n')
print(models.execute_kw(db, uid, password,
    'res.partner', 'search',
    [[['is_company', '=', True], ['customer', '=', True]]]))
print('\n-------------------------')

#Pagination
print('Pagination\n -------------------------\n')
print(models.execute_kw(db, uid, password,
    'res.partner', 'search',
    [[['is_company', '=', True], ['customer', '=', True]]],
    {'offset': 1, 'limit': 2}))
print('\n-------------------------')

#Count records
print('Count records\n -------------------------\n')
print(models.execute_kw(db, uid, password,
    'res.partner', 'search_count',
    [[['is_company', '=', True], ['customer', '=', True]]]))
print('\n-------------------------')

#Read records
print('Read records\n -------------------------\n')
ids = models.execute_kw(db, uid, password,
    'res.partner', 'search',
    [[['is_company', '=', True], ['customer', '=', True]]],
    {'limit': 1})
[record] = models.execute_kw(db, uid, password,
    'res.partner', 'read', [ids])
print('\n-------------------------')
print('Records\n -------------------------\n')
for elem in record:
    print(elem, ":", record[elem])
print('\n-------------------------')
print('Ids\n -------------------------\n')
print(ids)
print('\n-------------------------')
# count the number of fields fetched by default
print('Ids\n -------------------------\n')
print(len(record))
print('\n-------------------------')

#List record fields
print('List record fields\n -------------------------\n')
fields = models.execute_kw(
    db, uid, password, 'res.partner', 'fields_get',
    [], {'attributes': ['string', 'help', 'type']})
for elem in fields:
    print(elem, ":", fields[elem])
print('\n-------------------------')

#Search and read
print('Search and read \n -------------------------\n')
resultado = models.execute_kw(db, uid, password,
    'res.partner', 'search_read',
    [[['is_company', '=', True], ['customer', '=', True]]],
    {'fields': ['name', 'country_id', 'comment'], 'limit': 5})
for elem in resultado:
    print(elem)
print('\n-------------------------')


#Create record

print('Create record \n -------------------------\n')
npartner = input("Introduzca un nombre:")
nid = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
    'name': npartner,
}])
print("ID de", npartner, ":", nid)


print('\n-------------------------')

#Update record
print('Update record \n -------------------------\n')
npartner2 = input("Introduzca otro nombre para este usuario:")
print("Modificando", npartner, "a",npartner2, "...")
models.execute_kw(db, uid, password, 'res.partner', 'write', [[nid], {
    'name': npartner2
}])


print('\n-------------------------')

#Delete record
print('Delete record \n -------------------------\n')
print("Borrando a", npartner2)
models.execute_kw(db, uid, password, 'res.partner', 'unlink', [[nid]])
# check if the deleted record is still in the database
models.execute_kw(db, uid, password,
    'res.partner', 'search', [[['id', '=', nid]]])


print('\n-------------------------')

#Query que tiene 10 resultados

print('Ejecutando query... \n -------------------------\n')
resultado = models.execute_kw(db, uid, password,
    'res.partner', 'search_read',
    [[['customer', '=', True]]],
    {'fields': ['name', 'country_id', 'comment']})
for elem in resultado:
    print(elem)


print('\n-------------------------')

#Volcado en la BBDD

ndb = input("Introduzca el nombre de la base de datos:")
print("Volcando en", ndb)

#database connection
try:
    connection = pymysql.connect("localhost","root","",ndb )
except:
    print("Base de datos no encontrada")
cursor = connection.cursor()

TablaClientes = """CREATE TABLE Clientes(
ID INT(20) PRIMARY KEY AUTO_INCREMENT,
NAME  CHAR(40) NOT NULL,
COUNTRY_ID INT(10),
COMMENT VARCHAR(40))"""
try:
    cursor.execute(TablaClientes)
except(pymysql.err.InternalError):
    print("Atencion: tabla ya presente en la BBDD")
finally:
    for elem in resultado:
        cid = elem['country_id']
        if cid:
            cid = cid[0]
        else:
            cid = 0

        insert1 = "INSERT INTO Clientes(NAME, COUNTRY_ID, COMMENT) VALUES('{0}', '{1}', '{2}' );".format(elem['name'], cid, elem['comment'])

        cursor.execute(insert1)

    # some other statements  with the help of cursor
    connection.commit()
    connection.close()