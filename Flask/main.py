
from flask import Flask,render_template,request,redirect,session
import mysql.connector
import os
# from flask_sqlalchemy import SQLAlchemy,model
from flask import current_app

app=Flask(__name__)
app.secret_key=os.urandom(24)

# app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Abhishek9170@@localhost/testdb1'
# db=SQLAlchemy(app)
#
# class vehicles(db.Model):
#     __tablename__='vehicles_Authentication'
#     email=db.Column(db.String(100), primary_key = True)
#     password=db.Column(db.String(50))
#     # name=db.column(db.String(100))
#
#
# def __init__(self,email,password):
#     self.email=email
#     self.password=password
#
# @app.route('/login/',methods=['GET','POST'])
# def login_validation():
#     if request.method=='POST':
#         email=request.form['email']
#         password=request.form['password']
#
#         vehicles_Authentication=Vehicles_Authentication=(email,password)
#         db.session.add(vehicles_Authentication)
#         db.session.commit()

#
# app=Flask(__name__)
# conn=mysql.connector.connect(host=".......",user=".....",password="...",database="....")
# cursor=conn.cursor()



@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def about():
    return render_template("register.html")


@app.route('/')
def home():
    # if 'user_id' in session:
    #     return render_template('home.html')
    # else:
    #     return redirect('/')
     return render_template('home.html')


@app.route('/login_validation/',methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')
    # cursor.execute("""SELECT * FROM column_name WHERE email LIKE '{}' AND password LIKE '{}'"""
    #                .format(email,password))
    # users=cursor.fetchall()



    #     return redirect('/home')
    # else:
    #     return redirect('/')
    return "The email is {} and the password is {}".format(email, password)

@app.route('/add_user',methods=['POST'])
def add_user():
    name=request.form.get('uname')
    email=request.form.get('uemail')
    passowrd=request.form.get('upassword')
    #
    # cursor.execute(""" INSET INTO users(user_id,email,password) VALUES
    # (NULL,'{}','{}','{}'""".format(name,email,password))
    # conn.commit()

    # cursor.execute(""" SELECT * FROM Table_name WHERE email LIKE '{}'""".format(email))
    # myuser=cursor.fetchall()
    # session['user_id']=myuser[0][0]
    # return redirect('/home')
    return "User Register Successfully"

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

@app.route('/check')
def check():
    return render_template('check.html')

@app.route('/update')
def update():
    return render_template('update.html')

@app.route('/check_detail')
def check_detail():
    return render_template('check_detail.html')


if __name__=="__main__":
    app.run(debug=True)

