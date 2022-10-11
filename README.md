### ojitos369 (General)
[REPO: https://github.com/Ojitos369/ojitos369-pip](https://github.com/Ojitos369/ojitos369-pip)

### Databases

#### Oracle

```py

from ojitos369_oracle_db.oracle_db import ConexionOracle

db_data = {
    'user': 'your_db_user',
    'password': 'your_db_password',
    'host': 'your_db_host',
    'scheme': 'your_scheme_name',
}
conexion = ConexionOracle(db_data)

conexion.consulta(query, params=None) # return a list of list with the result of the query
# >> [["ojitos369", 18], ["ojitos369", 18]]
conexion.consulta_asociativa(query, params=None) # return a list of dict with the result of the query
# >> [{"name": "ojitos369", "age": 18}, {"name": "ojitos369", "age": 18}]
conexion.preparar_transaccion(query) # prepare transaction with query
# >> Bool
conexion.ejecutar(parametros = None) # execute transaction prepared with preparar_transaccion
# >> Bool

conexion.paginador(query, registros_pagina = 1, pagina = 2, params = None) # return de n resutls of query
# >> {
# >>     'registros': [{"name": "ojitos369", "age": 18, "rnum": 2}],
# >>     'num_registros': 2,
# >>     'paginas': 2,
# >>     'pagina': 2,
# >> }

conexion.commit() # commit transaction
conexion.rollback() # rollback transaction
conexion.close() # close connection

```