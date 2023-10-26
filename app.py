from datetime import datetime
import os
from flask import Flask, jsonify, render_template, request, redirect, session, url_for  
from flask_sqlalchemy import SQLAlchemy  
  
app = Flask(__name__)  
app.config['SECRET_KEY']=os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@192.168.1.186/wuyesys'  
db = SQLAlchemy(app)
  
class User(db.Model):  
    id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(50))  
    password = db.Column(db.String(50))  
    privilege= db.Column(db.Integer)
class Fix_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    content = db.Column(db.String(50))
    create_time=db.Column(db.Date())
    house_info=db.Column(db.Integer)
class Houses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50))
    phone=db.Column(db.String(11))
    address=db.Column(db.String(50))
    create_time=db.Column(db.Date())
    user_id=db.Column(db.Integer)
  
@app.route('/login', methods=['GET', 'POST'])  
def login():
    if request.method == 'POST':  
        username = request.form['username']
        password = request.form.get('password')
        user = User.query.filter_by(username=username,password=password).first()
        if user: 
            session['username']=user.username
            session['password']=user.password
            session['privilege']=user.privilege
            return redirect('index')
        else:  
            return render_template('login.html',message='error')
    return render_template('login.html')  
  
@app.route('/index',methods=['GET','POST'])
def index():
    username = session.get('username')
    if (username):
        if session.get('privilege')!=2:
            houses=Houses.query.all()
            for house in houses:
                house.username=User.query.filter_by(id=house.user_id).first().username
        else:
            user_id=User.query.filter_by(username=username).first().id
            houses=Houses.query.filter_by(user_id=user_id).all()
            for house in houses:
                house.username=username
        return render_template('index.html',houses=houses,username=username)
    return render_template('login.html')
@app.route('/logout')  
def logout():
    session['username']=None
    return render_template('login.html')

@app.route('/add',methods=['GET','POST'])
def add():
    if request.method == 'POST':
        name= request.form.get('name')
        phone=request.form.get('phone')
        address=request.form.get('address')
        create_time = datetime.now()
        create_time = create_time.strftime(f"%Y-%m-%d %H:%M:%S")
        user_id=User.query.filter_by(username=session.get('username')).first().id
        house = Houses(name=name,phone=phone,address=address,create_time=create_time,user_id=user_id)
        db.session.add(house)
        db.session.commit()
        return redirect('index')
    else:
        return render_template('add.html')
@app.route('/update',methods=['GET','POST'])
def update():
    if request.method=='GET':
        house = Houses.query.filter_by(id=request.args.get('id')).first()
        return render_template('update.html',house=house)
    else:
        id = request.args.get('id')
        name= request.form.get('name')
        phone=request.form.get('phone')
        address=request.form.get('address')
        house = Houses.query.filter_by(id=id).first()
        house.name=name
        house.phone=phone
        house.address=address
        db.session.commit()
        return redirect('index')
@app.route('/delete',methods=['GET'])
def delete():
    id = request.args.get('id')
    Houses.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect('index')
@app.route('/')  
def dashboard():  
    return redirect('index')

if __name__ == '__main__':  
    app.run(host='0.0.0.0',port='8080')