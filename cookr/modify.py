from flask import Blueprint, flash, g, redirect, render_template, request, url_for, Flask, jsonify
from werkzeug.exceptions import abort
from flask_login import current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField
from cookr.db import (get_db, close_db)
from pandas import isnull

bp = Blueprint('modify', __name__)
@bp.route('/mod')


@bp.route('/mod', methods=('GET','POST'))
def index():
  return render_template('home.html')


@bp.route('/mod/ref_id=<ref_id>', methods=('GET','POST'))
def mod_view(ref_id=None):
  if isnull(ref_id):
    return redirect(url_for('.index'),flash('INVALID REF_ID'))

  return render_template(
    'mod/index.html',
    rec_lst=rec_query(ref_id),
    ing_arr=ing_query(ref_id),
    step_arr=step_query(ref_id)
  )

#recipe query
def rec_query(ref_id=''):
  db=get_db()

  query=f'SELECT * FROM recipe WHERE id = {ref_id}'
  arr=db.execute(query).fetchone()
  rec=()
  rec.id=arr[0]
  rec.name=arr[1]
  rec.desc=arr[2]
  rec.time=arr[3]
  rec.temp=arr[4]
  rec.serv=arr[5]
  rec._org=arr[6]
  return rec

#ingredient query
def ing_query(ref_id=''):
  db=get_db()

  query=f'SELECT *, IFNULL(unit,"") as "unit2" FROM ingredients WHERE mod_id = {ref_id}'
  arr=db.execute(query).fetchall()
  return arr

#step query
def step_query(ref_id=''):
  db=get_db()

  query=f'SELECT * FROM steps WHERE mod_id = {ref_id}'
  arr=db.execute(query).fetchall()
  return arr

#@bp.route('mod/ref_id=<ref_id>/delete', methods=('GET','POST'))
#  db=get_db()

