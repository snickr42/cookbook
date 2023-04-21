from flask import Blueprint, flash, g, redirect, render_template, request, url_for, Flask, current_app
from werkzeug.utils import secure_filename
from werkzeug.exceptions import abort
from flask_login import current_user, login_user, logout_user, login_required
from satr.db import (get_db, close_db)
#import os
from pathlib import Path
import sqlite3
import pandas as pd
import csv

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

@login_required
@bp.route('/upld')
def index():
    return render_template('upld/index.html')

@login_required
@bp.route('/upld/file', methods=['POST'])
def file_upld():
    f = request.files['upld_fl']
    if f:
        fl_tmp = secure_filename(f.filename)
        upload_file = '{}/{}'.format(current_app.config['UPLD_DIR'],fl_tmp)
        f.save(upload_file)
        imprt_fl='{}/{}'.format(current_app.config['UPLD_DIR'],'upld_tmp.csv')
    else:
        err='ERROR: No file found'
        return redirect(url_for('.index'),flash('< None > {}'.format(err)))
    try:
        x2c(f,'Test Status',imprt_fl)
        upld_tr(imprt_fl)
        err='uploaded successfully'
        return redirect(url_for('.index'),flash('< {} > {}'.format(fl_tmp,err)))
    except:
        err='Error: File not supported'
        return redirect(url_for('.index'),flash('< {} > {}'.format(fl_tmp,err)))
    finally:
        Path(upload_file).unlink()

def x2c(wrbk,sht,save_fl):
    read_file = pd.read_excel(wrbk, sheet_name=sht)
    read_file.to_csv (save_fl, index = None, header=True)
    print(read_file) #debug
def upld_tr(imprt_fl):
    drp_tbl_query='DROP TABLE IF EXISTS import_results'
    crt_tbl_query='CREATE TEMPORARY TABLE IF NOT EXISTS import_results( \
sat_id TEXT, \
description TEXT, \
status TEXT, \
date DATE, \
tester TEXT, \
ne_type TEXT, \
ne_id TEXT, \
user TEXT, \
validation_comments TEXT, \
priority TEXT, \
sys_impact TEXT, \
admin_support TEXT, \
ffa_applicable TEXT, \
run_time TEXT, \
sat_version TEXT, \
subject TEXT, \
sat_test_scope_id INTEGER NOT NULL REFERENCES sat_test_scope(id), \
ref_id INTEGER NOT NULL REFERENCES sat_test(ref_id), \
sat_test_id INTEGER NOT NULL REFERENCES sat_test(id), \
tol_id INTEGER NOT NULL REFERENCES tol(id) \
)'

    db=get_db()
    #Connect to main db
    main_con = sql_connection(current_app.config['DATABASE'])
    main_db=main_con.cursor()

    #Create temporary import table. Import results to table
#    exct_qry(main_con,drp_tbl_query)
    exct_qry(main_con,crt_tbl_query)
    df = pd.read_csv(imprt_fl)
    df.to_sql('import_results',main_con,if_exists='append',index=False)
    #Get TOL ID
    tol_id=main_db.execute('SELECT tol_id FROM import_results LIMIT 1').fetchone()[0]
#    #debug
#    rows=main_db.execute('SELECT * FROM import_results LIMIT 10').fetchall()
#    for row in rows :
#        print(row)
#    except:
#        err='Error: temporary table creation/import failed'
#        print(err)
#        return redirect(url_for('.index'),flash('< {} > {}'.format(fl_tmp,err)))
    #Check whether test_status table already contains results for the TOL ID. If false, insert all results. If true, insert only updated values"
    tol_query=db.execute(f'SELECT * FROM test_status WHERE tol_id = {tol_id}').fetchall()
    tol_chck=len(tol_query)
    if tol_chck==0:
        upld_query='INSERT INTO test_status (status,date,tester,ne_id,user,validation_comments,sat_test_scope_id,ref_id,sat_test_id,tol_id) \
SELECT import_results.status,import_results.date,import_results.tester,import_results.ne_id,import_results.user,import_results.validation_comments,import_results.sat_test_scope_id,import_results.ref_id,import_results.sat_test_id,import_results.tol_id \
FROM import_results'
    else:
        upld_query=f'INSERT INTO test_status (status,date,tester,ne_id,user,validation_comments,sat_test_scope_id,ref_id,sat_test_id,tol_id) \
SELECT import_results.status,import_results.date,import_results.tester,import_results.ne_id,import_results.user,import_results.validation_comments,import_results.sat_test_scope_id,import_results.ref_id,import_results.sat_test_id,import_results.tol_id \
FROM import_results \
JOIN test_status ON \
import_results.status IS NOT test_status.status \
AND import_results.tol_id = test_status.tol_id AND import_results.sat_test_scope_id = test_status.sat_test_scope_id AND test_status.id IN (SELECT max(test_status.id) as id FROM test_status WHERE tol_id = {tol_id} GROUP BY sat_test_scope_id) \
OR \
import_results.date IS NOT test_status.date \
AND import_results.tol_id = test_status.tol_id AND import_results.sat_test_scope_id = test_status.sat_test_scope_id AND test_status.id IN (SELECT max(test_status.id) as id FROM test_status WHERE tol_id = {tol_id} GROUP BY sat_test_scope_id) \
OR \
import_results.validation_comments IS NOT test_status.validation_comments \
AND import_results.tol_id = test_status.tol_id AND import_results.sat_test_scope_id = test_status.sat_test_scope_id AND test_status.id IN (SELECT max(test_status.id) as id FROM test_status WHERE tol_id = {tol_id} GROUP BY sat_test_scope_id) \
OR \
import_results.user IS NOT test_status.user \
AND import_results.tol_id = test_status.tol_id AND import_results.sat_test_scope_id = test_status.sat_test_scope_id AND test_status.id IN (SELECT max(test_status.id) as id FROM test_status WHERE tol_id = {tol_id} GROUP BY sat_test_scope_id) \
OR \
import_results.ne_id IS NOT test_status.ne_id \
AND import_results.tol_id = test_status.tol_id AND import_results.sat_test_scope_id = test_status.sat_test_scope_id AND test_status.id IN (SELECT max(test_status.id) as id FROM test_status WHERE tol_id = {tol_id} GROUP BY sat_test_scope_id) \
OR \
import_results.tester IS NOT test_status.tester \
AND import_results.tol_id = test_status.tol_id AND import_results.sat_test_scope_id = test_status.sat_test_scope_id AND test_status.id IN (SELECT max(test_status.id) as id FROM test_status WHERE tol_id = {tol_id} GROUP BY sat_test_scope_id)'

    print(f'tol_chck: {tol_chck}') #debug
    print(upld_query)
    #Upload test results. Close connection
    exct_qry(main_con,upld_query)
    main_db.close()
