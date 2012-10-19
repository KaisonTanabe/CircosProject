from pymongo import Connection

pycircos_conn_args = {
    'host'  : 'alex.mongohq.com',
    'port'  : 10069,
}
pycircos_user_args = ('Scott', 'letmein')

def connect():
    connection = Connection(**pycircos_conn_args)
    db = connection.Pycircos
    db.authenticate(*pycircos_user_args)
    collection = db.Milham
    return db, collection

