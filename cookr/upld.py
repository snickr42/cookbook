from flask import Blueprint, flash, g, redirect, render_template, request, url_for, Flask, current_app
from werkzeug.utils import secure_filename
# from werkzeug.exceptions import abort
from flask_login import current_user, login_user, logout_user, login_required
# from cookr.db import (get_db, close_db)
#import os
from pathlib import Path
import sqlite3
import pandas as pd
# import csv

bp = Blueprint('upld', __name__)
ALLOWED_EXTENSIONS = {'xlsx'}



def sql_connection(sql_db,uri_val=None):
    if not uri_val:
        con = sqlite3.connect(sql_db, uri=uri_val)
    #else:
    #    con = sqlite3.connect(sql_db)
    #    print(f'Connection is established: Database is created in {sql_db}')
    return con

def exct_qry(con,query):
    cursorObj = con.cursor()
    cursorObj.execute(query)
    con.commit()

#def allowed_file(filename):
#    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @login_required
@bp.route('/upld')
def index():
    return render_template('upld/index.html')

# @login_required
@bp.route('/upld/file', methods=['POST'])
def file_upld():
    print(f'file_upld')

    f = request.files['upld_fl']
    if f:
        fl_tmp = secure_filename(f.filename)
        upload_file = '{}/{}'.format(current_app.config['UPLD_DIR'],fl_tmp)
        f.save(upload_file)
        print(f'f: {f}')
        print(f'upload_file: {upload_file}')
    else:
        err='ERROR: No file found'
        return redirect(url_for('.index'),flash('< None > {}'.format(err)))
    try:
        for sht in ['recipe','ingredient','step']:
            save_fl='{}/{}'.format(current_app.config['UPLD_DIR'],f'{sht}_upld_tmp.csv')
            x2c(upload_file,sht,save_fl)
            upld_tr(save_fl,sht)
            print(f'sheet: {sht}')
            print(f'save_fl: {save_fl}')
        err='uploaded successfully'
        return redirect(url_for('.index'),flash('< {} > {}'.format(fl_tmp,err)))
    except:
        err='Error: File not supported'
        return redirect(url_for('.index'),flash('< {} > {}'.format(fl_tmp,err)))
    finally:
        Path(upload_file).unlink()
    
def x2c(wrbk,sht,save_fl):
    read_file = pd.read_excel(wrbk, sheet_name=sht)
    read_file.to_csv(save_fl, index = None, header=True)

    print(read_file) #debug

def upld_tr(imprt_fl,sht):
    #Connect to main db
    main_con = sql_connection(current_app.config['DATABASE'])
    main_db=main_con.cursor()
    #Get last recipe id +1
    

    if sht=='recipe':
        recipe_id=main_db.execute('SELECT MAX(id) FROM recipe').fetchone()[0] + 1
        tmp_tbl='import_recipe'
        crt_query='CREATE TEMPORARY TABLE IF NOT EXISTS import_recipe( \
name TEXT, \
description TEXT, \
cooktime TEXT, \
cooktemp TXT, \
servings TEXT, \
notes TEXT, \
origin TEXT, \
date DATE DEFAULT CURRENT_DATE \
)'
        insrt_query=f'INSERT INTO recipe (id,name,description,cooktime,cooktemp,servings,notes,origin,date) \
SELECT {recipe_id}, {tmp_tbl}.name,{tmp_tbl}.description,{tmp_tbl}.cooktime,{tmp_tbl}.cooktemp,{tmp_tbl}.servings,{tmp_tbl}.notes,{tmp_tbl}.origin,{tmp_tbl}.date \
FROM {tmp_tbl}'
    elif sht=='ingredient':
        recipe_id=main_db.execute('SELECT MAX(id) FROM recipe').fetchone()[0]
        tmp_tbl='import_ingredients'
        crt_query='CREATE TEMPORARY TABLE IF NOT EXISTS import_ingredients( \
ingredient TEXT,\
quantity TEXT,\
unit TEXT,\
note TEXT,\
date DATE DEFAULT CURRENT_DATE\
)'
        insrt_query=f'INSERT INTO ingredients (recipe_id,ingredient,quantity,unit,note,date) \
SELECT {recipe_id},{tmp_tbl}.ingredient,{tmp_tbl}.quantity,{tmp_tbl}.unit,{tmp_tbl}.note,{tmp_tbl}.date \
FROM {tmp_tbl}'
    elif sht=='step':
        recipe_id=main_db.execute('SELECT MAX(id) FROM recipe').fetchone()[0]
        tmp_tbl='import_steps'
        crt_query='CREATE TEMPORARY TABLE IF NOT EXISTS import_steps( \
step Integer,\
description TEXT,\
note TEXT,\
date DATE DEFAULT CURRENT_DATE\
)'
        insrt_query=f'INSERT INTO steps (recipe_id,step,description,note,date) \
SELECT {recipe_id},{tmp_tbl}.step,{tmp_tbl}.description,{tmp_tbl}.note,{tmp_tbl}.date \
FROM {tmp_tbl}'

    #Create temporary import table. Import results to table
    exct_qry(main_con,crt_query)
    df = pd.read_csv(imprt_fl)
    df.to_sql(tmp_tbl,main_con,if_exists='append',index=False)
    
    print(insrt_query)
    #Upload test results. Close connection
    exct_qry(main_con,insrt_query)
    main_db.close()
