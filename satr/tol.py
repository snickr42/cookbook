from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Flask
)
from werkzeug.exceptions import abort
from flask_login import current_user, login_user, logout_user, login_required

from satr.db import (get_db, close_db)

bp = Blueprint('tol', __name__)

@bp.route('/tol')
@login_required
def index(tol_id=0):
    db=get_db()
    #menu_query='SELECT * FROM tol ORDER BY enter_date desc'
    table_query='SELECT * FROM tol_scope_view ORDER BY enter_date desc'
    #drpdwn=db.execute(menu_query).fetchall()
    tbl=db.execute(table_query).fetchall()
    close_db()
    return render_template(
      'tol/index.html',
      #drpdwn=drpdwn,
      tbl=tbl
    )

@bp.route('/tol/sys_release', methods=('GET','POST'))
@login_required
def sys_release():
    db=get_db()
    #sys_query='SELECT sys_release.major_release, sys_release.minor_release, tol_scope.sw_version, tol_scope.sw_id, tol_scope.tol_id FROM tol_scope JOIN sys_release ON tol_scope.sys_release_id=sys_release.id'
    sys_query='SELECT site_view.major_release, site_view.minor_release, tol_scope.sw_version, tol_scope.sw_id, site_view.system, site_view.env, tol.enter_date, tol.exit_date, tol.notes, tol_scope.tol_id FROM tol_scope JOIN site_view ON tol_scope.sys_release_id=site_view.sys_id JOIN tol WHERE tol_scope.tol_id=tol.id'
    sys_tbl=db.execute(sys_query).fetchall()
    
    return render_template(
      'tol/sys_release.html',
      sys_tbl=sys_tbl
    )

@bp.route('/tol/update', methods=('GET','POST'))
@login_required
def update():

    if request.method=='POST':
        tol_id=request.form['tol_select']
        return redirect(url_for('.summary', tol_id=tol_id))

@bp.route('/tol/<tol_id>/summary', methods=('GET','POST'))
@login_required
def summary(tol_id):
    db=get_db()
    tol_title_query='SELECT name FROM tol WHERE id = ' + tol_id
    tol_query='SELECT * FROM tol_scope_view WHERE tol_id = ' + tol_id
    tol_scope_query='SELECT * FROM tol_scope WHERE tol_id = ' + tol_id
    ne_query='SELECT ne_release FROM ne_release JOIN tol_scope ON ne_release_id = ne_release.id AND tol_id = ' + tol_id
    
    tol_list=db.execute(tol_query).fetchall()
    tol_scope_list=db.execute(tol_scope_query).fetchall()
    ne_list=db.execute(ne_query).fetchall()
    tol_title=db.execute(tol_title_query).fetchone()[0]
    stat_list=['Passed','Failed','Open','NT','Blocked','Removed']
    result_list=[]
    #loop through each ne type in tol
    for tmp_ne in ne_list:
        stat_dict={}
        ne_sum=0
        ne=tmp_ne[0]
        #assign temporary dictionary for each ne type. key value pairs store ne_release and status results
        stat_dict['ne_release']=ne
        for stat in stat_list:
            ne_query=f'SELECT COUNT(*) FROM test_status_view WHERE ne_release="{ne}" AND status="{stat}" AND test_status_id IN (SELECT max(test_status_id) FROM test_status_view WHERE tol_id="{tol_id}" GROUP BY sat_test_scope_id)'
            stat_dict[stat]=db.execute(ne_query).fetchone()[0]
            ne_sum+=stat_dict[stat]
        #'Removed' tests are not included in the total
        ne_sum-=stat_dict['Removed']
        stat_dict['Total']=ne_sum
        #result_list is a list of ne dictionaries
        result_list.append(stat_dict)
    #total up all status results. Running a new query is easier than re-looping through all the results
    total_sum=0
    total_dict={}
    total_dict['ne_release']='Total'
    for stat in stat_list:
        total_query=f'SELECT COUNT(*) FROM test_status_view WHERE status="{stat}" AND test_status_id IN (SELECT max(test_status_id) FROM test_status_view WHERE tol_id="{tol_id}" GROUP BY sat_test_scope_id)'
        total_dict[stat]=db.execute(total_query).fetchone()[0]
        total_sum+=total_dict[stat]
    total_sum-=total_dict['Removed']
    total_dict['Total']=total_sum
    result_list.append(total_dict)
    close_db()
    return render_template(
      'tol/summary.html',
      tol_title=tol_title,
      tol_list=tol_list,
      tol_scope_list=tol_scope_list,
      result_list=result_list,
      tol_id=tol_id
    )

@bp.route('/tol/<tol_id>/status', methods=('GET','POST'))
@login_required
def status(tol_id):

    menu_query="SELECT \
sat_test.sat_id AS  SAT_ID, \
sat_test.description AS Description, \
test_status.status AS Status, \
test_status.date, \
ne_release.ne_release AS ne_release, \
test_status.ne_id AS NE_ID, \
test_status.tester AS Tester, \
test_status.user AS Test_User, \
test_status.validation_comments AS Validation_Comments, \
tol.name AS TOL, \
max(test_status.id), \
test_status.tol_id, \
sat_test.id AS sat_test_id, \
sat_test_scope.id AS sat_test_scope_id \
FROM sat_test_scope \
JOIN sat_test, ne_release, test_status, tol \
ON \
sat_test.id = sat_test_scope.ref_id AND test_status.sat_test_scope_id = sat_test_scope.id \
AND \
ne_release.id = sat_test_scope.ne_release_id AND test_status.sat_test_scope_id = sat_test_scope.id \
AND \
tol_id = tol.id AND tol.id = {} \
GROUP BY \
sat_test_scope_id;".format(tol_id)

    db=get_db()
#        menu_query='SELECT * FROM tol_test_status_view WHERE tol_id = ' + tol_id
#        menu_query='SELECT * FROM test_status_view WHERE tol_id = ' + tol_id


    title_query='SELECT name FROM tol WHERE id = ' + tol_id
    tbl=db.execute(menu_query).fetchall()
    tol_title=db.execute(title_query).fetchone()[0]
    close_db()
    return render_template(
      'tol/status.html',
      tbl=tbl,
      tol_id=tol_id,
      tol_title=tol_title
    )

@bp.route('/tol/<tol_id>/history', methods=('GET','POST'))
@login_required
def history(tol_id):

    db=get_db()
    menu_query='SELECT * FROM test_status_view WHERE tol_id = ' + tol_id
    title_query='SELECT name FROM tol WHERE id = ' + tol_id
    tbl=db.execute(menu_query).fetchall()
    tol_title=db.execute(title_query).fetchone()[0]
    close_db()
    return render_template(
      'tol/history.html',
      tbl=tbl,
      tol_id=tol_id,
      tol_title=tol_title
    )


