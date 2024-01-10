import math
from ojitos369.utils import print_line_center as plc
import cx_Oracle

class ConexionOracle:
    def __init__(self, db_data, **kwargs):
        db_conn = cx_Oracle.connect(db_data['user'] + '/' + db_data['password'] + '@' + db_data['host'] + '/' + db_data['scheme'])
        # print('##### Activando DB #####')

        self.cursor = db_conn.cursor()
        self.db_conn = db_conn

        self.ce = None
        self.send_error = False
        self.raise_error = False
        self.closed = False

        for k in kwargs:
            setattr(self, k, kwargs[k])
    
    def local_base(func):
        def wrapper(*args, **kwargs):
            ele = args[0]
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ele.rollback()
                query = ele.query if hasattr(ele, 'query') else ''
                params = ele.params if hasattr(ele, 'params') else {}
                ce = ele.ce if hasattr(ele, 'ce') else None
                send_error = ele.send_error if hasattr(ele, 'send_error') else False
                raise_error = ele.raise_error if hasattr(ele, 'raise_error') else False
                
                if ce:
                    ex = Exception(f'{plc(query)}{plc(params)}{plc(str(e))}')
                    error = ce.show_error(ex, send_email=send_error)
                    print(error)
                if raise_error:
                    raise e
                else:
                    return False
        return wrapper

    @local_base
    def consulta(self, query, params=None):
        self.query = query
        self.params = params
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    @local_base
    def ejecutar_funcion(self, query, params=None):
        self.query = query
        self.params = params
        self.cursor.callproc(query, params)
        return True

    @local_base
    def consulta_asociativa(self, query, params=None):
        self.query = query
        self.params = params
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        descripcion = [d[0].lower() for d in self.cursor.description]
        resultado = [dict(zip(descripcion, linea)) for linea in self.cursor]
        return resultado

    @local_base
    def preparar_transaccion(self, query):
        self.query = query
        self.cursor.prepare(query)
        #print(self.cursor.statement)
        return True

    @local_base
    def ejecutar(self, params=None):
        self.params = params
        if not params:
            self.cursor.execute(None)
            # print(self.cursor.bindvars)
            return True
        else:
            if isinstance(params, dict):
                self.cursor.execute(None, params)
                # print(self.cursor.bindvars)
            elif isinstance(params, list):
                self.cursor.executemany(None, params)
                # print(self.cursor.bindvars)
            else:
                raise Exception('Parametros: tipo no valido')
            return True

    @local_base
    def paginador(self, query, registros_pagina=10, pagina=1, params=None):
        self.query = query
        self.params = params
        # print(query)
        if params:
            num_registros = len(self.consulta_asociativa(query, params))
        else:
            num_registros = len(self.consulta_asociativa(query))
        paginas = math.ceil(num_registros/registros_pagina)
        if paginas < pagina: pagina = paginas
        limite_superior = registros_pagina * pagina
        limite_inferior = limite_superior - registros_pagina + 1

        query = ''' SELECT *
                    FROM (SELECT a.*, ROWNUM rnum
                            FROM ({0}) A)
                    WHERE rnum BETWEEN {2} AND {1}
                '''.format(query,
                        limite_superior,
                        limite_inferior)
        self.query = query
        self.params = params
        if params:
            registros = self.consulta_asociativa(query, params)
        else:
            registros = self.consulta_asociativa(query)

        if num_registros < registros_pagina:
            pagina = 1
        return {
            'registros': registros,
            'num_registros': num_registros,
            'paginas': paginas,
            'pagina': pagina,
        }

    @local_base
    def commit(self):
        self.db_conn.commit()
        return True

    def rollback(self):
        self.db_conn.rollback()
        return True
    
    def close(self):
        if not self.closed:
            self.cursor.close()
            self.db_conn.close()
            self.closed = True
        return True
    
    def set_ce(self, ce):
        self.ce = ce
        return True

    def set_envio_errores(self, send_error):
        self.send_error = send_error
        return True

    def set_raise_error(self, raise_error):
        self.raise_error = raise_error
        return True

    def activar_envio_errores(self):
        self.send_error = True
        return True

    def activar_raise_error(self):
        self.raise_error = True
        return True

    def desactivar_envio_errores(self):
        self.send_error = False
        return True

    def desactivar_raise_error(self):
        self.raise_error = False
        return True

    def __del__(self):
        try:
            self.close()
        except:
            pass
        return True
