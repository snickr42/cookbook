from flask import Blueprint, flash, g, redirect, render_template, request, url_for, Flask
from werkzeug.exceptions import abort
from flask_login import current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField
from satr.db import (get_db, close_db)

bp = Blueprint('st_lib', __name__)

@bp.route('/st_lib')
@login_required
def index():
    db=get_db()
    test_query='SELECT * FROM st_lib_view WHERE state="Active"'
    tbl=db.execute(test_query).fetchall()    
    hd_tbl=db.execute(test_query)
    for x in hd_tbl.description:
        #print(x[0])
        tbl_hdr=x[0]
    return render_template(
      'st_lib/index.html',
      tbl=tbl,
      tbl_hdr=tbl_hdr
    )

#@bp.route('/st_lib/update', methods=(['POST']))
#def update(): 
#    s_form=SearchForm(request.form)
#    if s_form.search_str.data:
#        field=request.form['field_slct']
#        search_str=s_form.search_str.data
#        return redirect(url_for('.search_result',field=field,search_str=search_str))
#    else:
#        error = ' \"BLANK Entry\" - Invalid Search'
#        return redirect(url_for('.index',error=error))

@bp.route('/st_lib/search_result/field=<field>&search_str=<search_str>', methods=('GET','POST'))
@login_required
def search_result(field,search_str):
    db=get_db()
    operator='='
    if field=='ref_id':
        search_field='ref_id'
    elif field=='sat_test_id':
        search_field='SAT_ID'
    elif field=='description':
        search_field='Description'
        operator='LIKE'
        search_str='%{}%'.format(search_str)
#    search_query='SELECT * from satr_test_search_view WHERE {} {} \"{}\"'.format(search_field,operator,search_str)
    search_query=f'SELECT * from st_lib_view WHERE {search_field} {operator} \"{search_str}\"'
    tbl=db.execute(search_query).fetchall()
    close_db()

    if len(tbl)==0:
        error =f'\"{search_str}\" - Invalid Search'
        return render_template(
          'st_lib/index.html',
          error=error
        )
    else:
        pass
    return render_template(
#      'st_lib/search_result.html',
      'st_lib/index.html',
      tbl=tbl
    )

@bp.route('/st_lib/detail/ref_id=<ref_id>', methods=('GET','POST'))
@login_required
def st_detail(ref_id):
    db=get_db()
    st_query=f'SELECT * FROM sat_test WHERE ref_id = {ref_id}'
    scope_query=f'SELECT ne_release FROM ne_release WHERE id IN (SELECT ne_release_id FROM sat_test_scope WHERE ref_id={ref_id} AND state="Active")'
    hist_query=f'SELECT * FROM satr_test_search_view WHERE ref_id={ref_id} ORDER BY date DESC'
    
    st_tbl=db.execute(st_query).fetchall()
    scope_tbl=db.execute(scope_query).fetchall()
    hist_tbl=db.execute(hist_query).fetchall()

#    for st in st_tbl:
#        print(*st)
    for sc in scope_tbl:
        print(*sc)         
    for hs in hist_tbl:
        print(*hs)
    
    hd_query=db.execute(f'SELECT sat_id,description FROM sat_test WHERE ref_id={ref_id} AND state="Active" ORDER BY id DESC LIMIT 1').fetchone()
    sat_id=hd_query[0]
    sat_desc=hd_query[1]
    
    return render_template(
      'st_lib/detail.html',
      sat_id=sat_id,
      description=sat_desc,
      st_tbl=st_tbl,
      scope_tbl=scope_tbl,
      hist_tbl=hist_tbl
    )


#class SearchForm(FlaskForm):
#    field_str=StringField('field_str', validators=[DataRequired()])
#    search_str=StringField('search_str', validators=[DataRequired()])
