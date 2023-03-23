import math
from ojitos369.utils import print_line_center as plc
import cx_Oracle

class ConexionOracle:
    def __init__(self, db_data, ce = None):
        db_conn = cx_Oracle.connect(db_data['user'] + '/' + db_data['password'] + '@' + db_data['host'] + '/' + db_data['scheme'])
        # print('##### Activando DB #####')

        self.cursor = db_conn.cursor()
        self.db_conn = db_conn
        self.ce = ce

    def consulta(self, query, params=None, send_error=False, raise_error=False):
        self.query = query
        self.params = params
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            if self.ce:
                ex = Exception(f'{plc(str(e))}{plc(self.query)}{plc(self.params)}')
                error = self.ce.show_error(ex, send_email=send_error)
                print(error)
            if raise_error:
                raise e
            else:
                return False

    def ejecutar_funcion(self, query, params = None, send_error=False, raise_error=False):
        self.query = query
        self.params = params
        try:
            try:
                self.cursor.callproc(query, params)
                return True
            except Exception as e:
                # ex = Exception(f'''\n\n\nerror:\n{str(e)}\n\n\n\n\n\nquery:\n{str(self.query)}\n\n\n\n\n\nparams:\n{str(self.params)}\n\n\n''')
                # print(str(ex))
                # show_error(ex, send_email = True)
                print(e)
                self.db_conn.rollback()
                return False
        except Exception as e:
            if self.ce:
                ex = Exception(f'{plc(str(e))}{plc(self.query)}{plc(self.params)}')
                error = self.ce.show_error(ex, send_email=send_error)
                print(error)
            if raise_error:
                raise e
            else:
                return False

    def consulta_asociativa(self, query, params=None, send_error=False, raise_error=False):
        self.query = query
        self.params = params
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            descripcion = [d[0].lower() for d in self.cursor.description]
            # print(descripcion)
            resultado = [dict(zip(descripcion, linea)) for linea in self.cursor]
            # print(resultado)
            return resultado
        except Exception as e:
            if self.ce:
                ex = Exception(f'{plc(str(e))}{plc(self.query)}{plc(self.params)}')
                error = self.ce.show_error(ex, send_email=send_error)
                print(error)
            if raise_error:
                raise e
            else:
                return False

    def preparar_transaccion(self, query, send_error=False, raise_error=False):
        self.query = query
        try:
            try:
                self.cursor.prepare(query)
                #print(self.cursor.statement)
                return True
            except Exception as e:
                # ex = Exception(f'''\n\n\nerror:\n{str(e)}\n\n\n\n\n\nquery:\n{str(self.query)}\n\n\n\n\n\nparams:\n{str(self.params)}\n\n\n''')
                # print(str(ex))
                # show_error(ex, send_email = True)
                print(e)
                self.db_conn.rollback()
                return False
        except Exception as e:
            if self.ce:
                ex = Exception(f'{plc(str(e))}{plc(self.query)}{plc(self.params)}')
                error = self.ce.show_error(ex, send_email=send_error)
                print(error)
            if raise_error:
                raise e
            else:
                return False

    def ejecutar(self, params=None, send_error=False, raise_error=False):
        self.params = params
        try:
            try:
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
            except Exception as e:
                # ex = Exception(f'''\n\n\nerror:\n{str(e)}\n\n\n\n\n\nquery:\n{str(self.query)}\n\n\n\n\n\nparams:\n{str(self.params)}\n\n\n''')
                # print(str(ex))
                # show_error(ex, send_email = True)
                print(e)
                self.db_conn.rollback()
                return False
        except Exception as e:
            if self.ce:
                ex = Exception(f'{plc(str(e))}{plc(self.query)}{plc(self.params)}')
                error = self.ce.show_error(ex, send_email=send_error)
                print(error)
            if raise_error:
                raise e
            else:
                return False

    def paginador(self, query, registros_pagina=10, pagina=1, params=None, send_error=False, raise_error=False):
        self.query = query
        self.params = params
        try:
            try:
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
            except Exception as e:
                # ex = Exception(f'''\n\n\nerror:\n{str(e)}\n\n\n\n\n\nquery:\n{str(self.query)}\n\n\n\n\n\nparams:\n{str(self.params)}\n\n\n''')
                # print(str(ex))
                # show_error(ex, send_email = True)
                print(e)
                return False
        except Exception as e:
            if self.ce:
                ex = Exception(f'{plc(str(e))}{plc(self.query)}{plc(self.params)}')
                error = self.ce.show_error(ex, send_email=send_error)
                print(error)
            if raise_error:
                raise e
            else:
                return False

    def commit(self):
        try:
            self.db_conn.commit()
            return True
        except Exception as e:
            # ex = Exception(f'''\n\n\nerror:\n{str(e)}\n\n\n\n\n\nquery:\n{str(self.query)}\n\n\n\n\n\nparams:\n{str(self.params)}\n\n\n''')
            # print(str(ex))
            # show_error(ex, send_email = True)
            print(e)
            self.db_conn.rollback()
            return False

    def rollback(self):
        self.db_conn.rollback()
        return True
    
    def close(self):
        self.db_conn.close()
        return True

