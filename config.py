import os
base_dir = os.path.abspath(os.path.dirname(__file__))
inst_dir=f'{base_dir}/instance'
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DATABASE=os.path.join(inst_dir, 'recipe.db')
#    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(inst_dir, 'usr_space.db')
#    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLD_DIR=os.path.join(inst_dir, 'upld')

