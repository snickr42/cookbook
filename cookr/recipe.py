from flask import Blueprint, flash, g, redirect, render_template, request, url_for, Flask, jsonify
from werkzeug.exceptions import abort
from flask_login import current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField
from cookr.db import (get_db, close_db)

bp = Blueprint('recipe', __name__)
@bp.route('/recipe')

def index():
    db=get_db()
    test_query='SELECT * FROM recipe'
    tbl=db.execute(test_query).fetchall()    
    hd_tbl=db.execute(test_query)
    for x in hd_tbl.description:
        tbl_hdr=x[0]
    return render_template(
      'recipe/index.html',
      tbl=tbl,
      tbl_hdr=tbl_hdr
    )

@bp.route('/recipe/summary/ref_id=<ref_id>', methods=('GET','POST'))
def summary(ref_id=''):
  db=get_db()
  rec_query=f'SELECT * FROM recipe WHERE id = {ref_id}'
  ing_query=f'SELECT *, IFNULL(unit,"") as "unit2" FROM ingredients WHERE recipe_id = {ref_id}'
  step_query=f'SELECT * FROM steps WHERE recipe_id = {ref_id}'

  rec_tbl=db.execute(rec_query).fetchone()
  ing_tbl=db.execute(ing_query).fetchall()
  step_tbl=db.execute(step_query).fetchall()
  return render_template(
    'recipe/summary.html',
    rec_tbl=rec_tbl,
    ing_tbl=ing_tbl,
    step_tbl=step_tbl
  )

@bp.route('/recipe/java', methods=('GET','POST'))
def java():
  if request.method=='GET':
    return render_template(
      'java.html',
    )
  elif request.method=='POST':
    print("## POSTING ##")
    data="[1,2,3,4,5]"
    return "[1,2,3,4,5]"

