import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext



class sql_db_class:
    def __init__(self,db_name=None):
        if db_name:
            self.db_name=db_name
        else:
            self.db_name=current_app.config['DATABASE']
        self.sql_db = sqlite3.connect(
          self.db_name,
          detect_types=sqlite3.PARSE_DECLTYPES
        )

    def init_db(self,sql_db,uri_val=None):
	if uri_val:
		con = sqlite3.connect(sql_db, uri=uri_val)
	#else:
	#    con = sqlite3.connect(sql_db)
	#    print(f'Connection is established: Database is created in {sql_db}')
	return con

    def exct_qry(query):
        cursorObj = con.cursor()
        cursorObj.execute(query)
        con.commit()
