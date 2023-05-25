
from flask import Flask,render_template,request,redirect,session, url_for, flash
from dotenv import load_dotenv, find_dotenv
import os
import twilio
import random
import string
import smtplib
from twilio.rest import Client
from pymongo import MongoClient
from  flask_pymongo import PyMongo
import bcrypt
from flask import current_app

#project name = A keyless secure anti-theft vehicle identification mechanism in iov
load_dotenv(find_dotenv())
password = os.environ.get("MONGODB_PWD")

app=Flask(__name__)
app.secret_key=os.urandom(24)

#app.config['MONGO_DBNAME'] = 'test'
app.config['MONGO_URI'] = f"mongodb+srv://Authentication_User4:AuthenticationUser1234@cluster0.dylrtop.mongodb.net/Project"
mongo = PyMongo(app)
#...............................................................................................................

#twilio config..................................................................................................
account_sid = 'AC58dd376f1c965d3d57e44bdc598c2901'
auth_token = 'ca913d83b940fbb1a013313139b0c9a9'
#...............................................................................................................

#Registration...................................................................................................
@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name':request.form['name']})
        
        if existing_user == None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'name':request.form['name'], 'password': hashpass, 'email': request.form['email'] })
            session['username'] = request.form['name']
            flash("You are logged in successfully","success")
            return render_template('Update.html')
        else:
            flash("The username already exists!","danger")
        
    return render_template("register.html")

#Login...........................................................................................................

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/update_login', methods = ['POST','GET'])
def update_login():
    users = mongo.db.users
    login_user = users.find_one({'email':request.form.get('email',False)})
    
    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form.get('name', False)
            flash("You are logged in successfully","success")
            return render_template('Update.html')
        
    flash("Invalid username/password combination","danger")   
    return render_template('login.html')
#....................................................................................................................


#Check...............................................................................................................
@app.route('/check', methods =  ['POST','GET'])
def check():
    if request.method == 'POST':
        project = mongo.db.project
        exist = project.find_one({'VIN':request.form['number']})
        if exist != None:
            session['v_name'] = request.form['number']
            return redirect(url_for('check_detail'))
        else:
            flash("Vehicle_id is not registered","danger")
    return render_template('check.html')


@app.route('/check_detail', methods = ['GET','POST'])
def check_detail():
    if request.method == 'POST':
        project = mongo.db.project
        if 'v_name' in session:
            #input1 = {'VIN' :request.form['number']}
            input1 = {'VIN' :session['v_name']}
            inputs = {
                'Engine': request.form['Engine'],
                'radiator': request.form['Radiator'],
                'fuel tank': request.form['Fuel'],
                'gear box': request.form['Gear'],
                'battery': request.form['Battery'],
                'rim': request.form['Rim']
            }
            counter = 0
            
            for key, value in inputs.items():
                result = project.find({key: value},{'_id':0})
                count = project.count_documents({key:value})
                if count != 0:
                    for res in result:
                        print(res)
                        if res:
                            if input1['VIN'] == res['VIN']:
                                flash(f"Match found for {key}!", 'success')
                            else:
                                phone = res['Phone no']
                                msg = f"Your part has been placed in some other vehicle having details: {res}"
                                message(phone,msg)
                                flash(f"Part Stolen for {key}!", 'danger')
                else:
                    flash(f"No match found for {key}!", 'danger')
                counter += 1
            session.pop('v_name')
            if counter == len(inputs):
                return render_template('check_detail.html')
             
    return render_template('check_detail.html')
#....................................................................................................................




#OTP generation.......................................................................................................
def generate_otp():
    otp_ = random.randint(1000, 9999)
    return str(otp_)
#.....................................................................................................................

#OTP over phone .....................................................................................................
def otp_phone(email_phone,otp_number):
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(from_='+12707704087',
        body=f"Your OTP is: {otp_number}",
        to='+91'+str(email_phone))
    print(message.sid)
    
#......................................................................................................................  

#OTP over mail..........................................................................................................  
def otp_mail(email_phone,otp_number):
    email_address = "authenticationuser4@gmail.com"
    email_password = "kdtgqumtvltduxmn"
    to_address = str(email_phone)
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_address, email_password)

        message = f"Subject: Your OTP is {otp_number}\n\nYour OTP is {otp_number}."
        server.sendmail(email_address, to_address, message)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server.quit()
#.......................................................................................................................

#Sending OTP.............................................................................................................
@app.route('/sends_otp',methods=['POST','GET'])
def sends_otp():
    if request.method == 'POST':
        email_phone = request.form['email_phone']
        method_ = request.form['method_']
        OTP = generate_otp()
        OTP_str = str(OTP)
            
        if method_ == 'email':
            otp_mail(email_phone,OTP_str)
            session['otp_number'] = OTP_str
            flash('OTP sent successfully!', 'success')
            return render_template('otp_verify.html')
        elif method_ == 'phone':
            otp_phone(email_phone,OTP_str)
            session['otp_number'] = OTP_str
            flash('OTP sent successfully!', 'success')
            return render_template('otp_verify.html')
    return render_template('sends_otp.html')
#.................................................................................................................    

#Verifying OTP ..................................................................................................   
@app.route('/otp_verify',methods=['POST','GET'])
def otp_verify():
    if 'otp_number' not in session:
        flash('OTP not found!', 'danger')
        return render_template('sends_otp.html')
    if request.method == 'POST':
        otp =request.form['otp']
        otp_code = session['otp_number']
        
        if otp == otp_code:
            session.pop('otp_number')
            return render_template('update_details.html')
        else:
            flash("Incorrect OTP! Please try again...",'danger')
            return render_template('otp_verify.html')
            
    return render_template('otp_verify.html')   
#.....................................................................................................................

#Updating.............................................................................................................
@app.route('/update',methods=['POST','GET'])
def update():
    if request.method == 'POST':
        project = mongo.db.project
        exist = project.find_one({'VIN':request.form['number']})
        if exist != None:
            session['vname'] = request.form['number']
            return redirect(url_for('sends_otp'))
        else:
            flash("Vehicle_id is not registered","danger")
    return render_template('Update.html')

@app.route('/update_details', methods=['POST','GET'])
def update_details():
    if request.method == 'POST':
        project = mongo.db.project
        if 'vname' in session:
            VIN = session['vname']
            part = request.form['part']
            part_id = request.form['part_id']
            updates = {"$set":{part:part_id}} 
            project.update_one({'VIN':VIN},updates)
            flash(f"The part id  for {part} is updated successfully",'success')
            session.pop('vname')
            return render_template('update_details.html')
    return render_template('update_details.html')
#....................................................................................................................

#Message to be send on checking......................................................................................
def message(phone,msg):
  client = Client(account_sid, auth_token)
  
  message = client.messages.create(
      from_='+12707704087',
      body=msg,
      to='+91'+str(phone)
      )
  print(message.sid)
  
#........................................................................................................................

#Trash: May be required later......................................................................................
@app.route('/')
def home():
    # if 'user_id' in session:
    #     return render_template('home.html')
    # else:
    #     return redirect('/')
     return render_template('home.html')


@app.route('/login_validation/',methods=['POST','GET'])
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


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')
#................................................................................................................. 



if __name__=="__main__":
    app.run(debug=True)

