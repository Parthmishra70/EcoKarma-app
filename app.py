# All packages 

from flask import Flask, render_template, request,session,redirect,flash,url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from uuid import uuid4
from random import randint
from twilio.rest import Client
from werkzeug.utils import secure_filename
import os
import qrcode

# sys
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/Swmuser'
app.config['SECRET_KEY'] = "Your_secret_string"

db = SQLAlchemy(app)


# twilio keys
account_sid = 'AC2c96f239700ae59d35459d684828a6d0'
auth_token = '1ec928077451ee1165ce95adf83ef37a'
client = Client(account_sid, auth_token)



# database
class emp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=False)
    area = db.Column(db.String(80), nullable=False)
    payment = db.Column(db.String(80), nullable=True)
    img = db.Column(db.String(80), nullable=True)
    date = db.Column(db.String(12), nullable=False)

# for the employee
class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(80), nullable=False)
    otp = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(80), nullable=False)
    Aimg = db.Column(db.String(80), nullable=False)
    img = db.Column(db.String(80), nullable=True)
    qr = db.Column(db.String(80), nullable=True)
    date = db.Column(db.String(12), nullable=False)

# for the products
class userapp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    category = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(80), nullable=True)
    price = db.Column(db.Integer, nullable=True)
    token = db.Column(db.String(80), nullable=True)
    area = db.Column(db.String(80), nullable=False)
    itemnames = db.Column(db.String(80), nullable=False)
    itemquantities = db.Column(db.String(80), nullable=False)
    itemprice = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(80), nullable=False)
    empname = db.Column(db.String(80), nullable=True)
    empphone = db.Column(db.String(80), nullable=True)
    otp = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    mode = db.Column(db.String(70), nullable=True)


# for the employee
class qrp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(80), nullable=False)
    collectedm = db.Column(db.String(80), nullable=False)
    perkg = db.Column(db.String(80), nullable=False)
    empphone = db.Column(db.String(80), nullable=True)
    date = db.Column(db.String(12), nullable=False)


# for the contct
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(80), nullable=False)
    msg = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(12), nullable=False)
    

# for the user index
@app.route("/")
def home():
    if 'user' in session:
        Userapp = userapp.query.filter_by(phone=session['phoneU']).all()
        User = user.query.filter_by(phone=session['phoneU']).first()
        return render_template('profile.html',req=Userapp,useri=User,username = session['user'],qr_code_name=User.qr)
    return redirect('/signin')

# for the user flash msg
@app.route("/usernotifi.")
def usernotifiction():  
    if 'user' in session:
        Userapp = userapp.query.filter_by(phone=session['phoneU']).all()
        User = user.query.filter_by(phone=session['phoneU']).first()
        return render_template('profile.html', success="Your request has been successfully submitted.",req=Userapp,useri=User,username = session['user'])
   
# for the user request form
@app.route("/userR", methods=['GET', 'POST'])
def userRequest():
    # Check if the user is logged in (you might need to set the 'user' session variable somewhere)
    if 'user' in session and session['user'] is not None:
        Userapp = userapp.query.filter_by(phone=session['phoneU']).first()
        User = user.query.filter_by(phone=session['phoneU']).first()

        if request.method == 'POST':
            name = request.form.get('name')
            address = request.form.get('address')
            area = request.form.get('area')
            phone = request.form.get('phone')
            itemnames = request.form.get('itemnames')
            itemprice = request.form.get('itemprice')
            itemquantities = request.form.get('itemquantities')
            otp = str(randint(0, 99999)).zfill(5)  # Generate a 5-digit OTP

            try:
                empA = emp.query.filter_by(area=area.lower()).first()
                if empA:
                    token = uuid4()
                    entry = userapp(
                        name=name, 
                        phone=phone, 
                        address=address, 
                        category=itemnames,
                        itemnames=itemnames,
                        itemquantities=itemquantities,
                        itemprice=itemprice, 
                        date=datetime.now(), 
                        token=token,
                        otp=otp,
                        mode="pending",
                        empphone=empA.phone,
                        area=area
                    )
                    
                    db.session.add(entry)
                    db.session.commit()

                    # Send a message to the employee
                    message_to_employee = client.messages.create(
                        from_='+16562186499',
                        body=f'This is your work on {address}.',
                        to=f'+91{empA.phone}'
                    )

                    # Send OTP to the user
                    message_to_user = client.messages.create(
                        from_='+16562186499',
                        body=f'This is your one-time password (OTP) for employee confirmation: {otp}. Please keep it confidential.',
                        to=f'+91{phone}'
                    )

                    # Redirect to a different page (GET request) to prevent data resubmission
                    return redirect('/usernotifi.   ')
                Userapp = userapp.query.filter_by(phone=session['phoneU']).all()
                return render_template('profile.html', error="No employee found for the specified area.", req=Userapp, useri=User, username=session['user'])

            except Exception as e:
                # Handle database errors gracefully
                print(f"An error occurred: {e}")
                return render_template('profile.html', error="An error occurred while processing your request.", req=Userapp, useri=User, username=session['user'])
        else:
            # Render the profile page for GET requests
            return render_template('profile.html', req=Userapp, useri=User, username=session['user'])
    else:
        # User is not logged in
        return render_template('login.html', error="You must be logged in to make a request.", req=Userapp, useri=User, username=session['user'])
    

# for the user resend code 
@app.route("/Resendcode")
def Resendcode():
    # Check if the user is logged in (you might need to set the 'user' session variable somewhere)
    if 'phoneE' in session and session['phoneE'] is not None:
        Userapp = userapp.query.filter_by(phone=session['phoneU']).first()
        User = user.query.filter_by(phone=session['phoneU']).first()
        db.session.commit()
        otp = randint(000000,999999)
        # Send OTP to the user
        Userapp.otp = otp
        db.session.commit()
        message_to_user = client.messages.create(
                        from_='+16562186499',
                        body=f'This is your one-time password (OTP) for employee confirmation: {otp}. Please keep it confidential.',
                        to=f'+91{User.phone}'
                    )

                    # Redirect to a different page (GET request) to prevent data resubmission
        return redirect("/empindex")
    else:
        # User is not logged in
        return redirect("/")


# for the user Adhar card
@app.route("/userup", methods=["POST","GET"])
def userup():
    if 'file1' in request.files:
        image = request.files['file1']
        print(f"\n\n\n\n\n\n\n ghsldlbsdlbjgundlbnslfgdbjh\n\n\n\n\n\n\n")
        if image.filename != '':
            # Extract the file extension from the original filename
            filename, file_extension = os.path.splitext(image.filename)

            # Generate a secure filename
            r = session['user']
            custom_filename = secure_filename(f'user{r}_{randint(000000,999999)}')  # Customize this naming scheme

            # Create the new filename by appending the original extension
            new_filename = custom_filename + file_extension

            # Determine the file path for the uploaded image
            image_path = os.path.join('/home/parth/Desktop/project2/myenv/static/aadhar', new_filename)
            image.save(image_path)
            
            try:
                # Get other product information from the form
                User = user.query.filter_by(phone=session['phoneU']).first()
                Userapp = userapp.query.filter_by(phone=session['phoneU']).all()
                # Emp = emp.query.filter_by(phone=session['phoneE']).first()
                        # Add the entry to the database, including the image filename
                if 'user' in session:
                    User.Aimg=new_filename  # Add this field for the image filename
                    db.session.commit()
                    message = client.messages.create(
                        from_='+917041170952',
                        body=f'AADHAR CARD COMES',
                        to=f'+91{User.phone}'
                    )













                    return render_template("profile.html", error="Done here",useri=User,req=Userapp)
            except Exception as e:
                return render_template("profile.html", error=e,useri=User,req=Userapp)
            
    else:
        return redirect("/")



# for the user Qr gen
@app.route("/Qr", methods=["POST", "GET"])
def QrP():
    if 'user' in session:
        data = session['phoneU']
        if data:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            qr_code_name = f"{data}_Qr.png"
            User = user.query.filter_by(phone=session['phoneU']).first()
            User.qr = qr_code_name
            db.session.commit()
            img.save(f'static/Qr/{qr_code_name}')
            Userapp = userapp.query.filter_by(phone=session['phoneU']).all()

            return render_template('profile.html',success="Done",req=Userapp,useri=User,username = session['user'],qr_code_name=qr_code_name)
        else:
            return redirect("/sigin")


# for the user ech Qr gen
@app.route("/Qr/<string:phone>", methods=["POST", "GET"])
def QriP(phone):
    if 'phoneE' in session:
        if request.method == 'POST':
            User = user.query.filter_by(phone=session['phoneU']).first()
            name = User.name
            phone = User.phone
            perkg = request.form.get('perkg')
            collectedm = request.form.get('perkg')
            empphone =  session['phoneE']
            entry = qrp(name=name, phone=phone,perkg=perkg,collectedm=collectedm,empphone=empphone, date= datetime.now())
            db.session.add(entry)
            db.session.commit()

            return redirect('/')
        else:
            return render_template("wetform.html",P = phone,Empi=Emp,username = session['phoneE'])


# for the employee signin
@app.route("/empindex")
def EMPhome():
    if 'phoneE' in session:
        Userapp = userapp.query.filter_by(empphone=session['phoneE']).all()
        Emp = emp.query.filter_by(phone=session['phoneE']).first()
        return render_template('empindex.html',req=Userapp,Empi=Emp,username = session['phoneE'])
    return redirect('/signin')

# edit user request form of empolyeees
@app.route("/editE/<string:token>", methods = ['GET', 'POST'])
def editE(token):
    if 'phoneE' in session:
        Userapp = userapp.query.filter_by(token=token).first()
        Emp = emp.query.filter_by(phone=session['phoneE']).first()
        if request.method == 'POST':
                otp = request.form.get('otp')
                itemnames = request.form.get('itemnames')
                itemprice = request.form.get('itemprice')
                itemquantities = request.form.get('itemquantities')
                Userapp = userapp.query.filter_by(otp=otp).first()
                if Userapp:
                    Userapp.itemnames = itemnames
                    Userapp.itemquantities = itemquantities
                    Userapp.itemprice = itemprice
                    Userapp.date= datetime.now()
                    Userapp.mode= "verify"

                else:
                    return redirect("/empindex")
                try:
                    db.session.commit()
                    message = client.messages.create(
                        from_='+16562186499',
                        body=f'This is your money: {itemprice}. Your money will be available in 5 days in your account.',
                        to=f'+91{Userapp.phone}'
                    )
                    message = client.messages.create(
                        from_='+16562186499',
                        body=f'This work was successfully done. The next work comes soon',
                        to=f'+91{Userapp.empphone}'
                    )
                    # Redirect to a different page (GET request) to prevent data resubmission
                    return redirect('/empindex')
                except Exception as e:
                    # Handle database errors gracefully
                    print(f"\n\n\n\n\n\n{e}\n\n\n\n\n\n")
                    return render_template('empindex.html', error="An error occurred while processing your request.",req=Userapp,Empi=Emp,username = session['phoneE'])
           
    return render_template('editp.html',req=Userapp,Empi=Emp,username = session['phoneE'])



# Define the directory where you want to store the uploaded images
upload_folder = '/home/parth/Desktop/project2/myenv/static/userimg'

@app.route("/uploader", methods=["POST"])
def uploader():
    if 'file1' in request.files:
        image = request.files['file1']

        if image.filename != '':
            # Extract the file extension from the original filename
            filename, file_extension = os.path.splitext(image.filename)

            # Generate a secure filename
            custom_filename = secure_filename(f'user_image{randint(000000,999999)}')  # Customize this naming scheme

            # Create the new filename by appending the original extension
            new_filename = custom_filename + file_extension

            # Determine the file path for the uploaded image
            if 'user' in session:
                image_path = os.path.join('/home/parth/Desktop/project2/myenv/static/userimg', new_filename)
                image.save(image_path)
            if 'phoneE' in session:
                upload_folder = '/home/parth/Desktop/project2/myenv/static/empimg'
                image_path = os.path.join(upload_folder, new_filename)
                image.save(image_path)


                # Get other product information from the form
           

            try:
                    # Add the entry to the database, including the image filename
                if 'user' in session:
                    User = user.query.filter_by(phone=session['phoneU']).all()
                    Userapp = userapp.query.filter_by(phone=session['phoneU']).all()
                    User.img=new_filename  # Add this field for the image filename
                    db.session.commit()
                    return redirect("/")
                    
                if 'phoneE' in session:
                    Emp = emp.query.filter_by(phone=session['phoneE']).first()

                    Emp.img=new_filename  # Add this field for the image filename
                    db.session.commit()
                    return redirect("/empindex")
            except Exception as e:
                    print(f"\n\n\n\n\n\n\n\nerrot: {e} \n\n\n\n\n\n\n\n")
                    return render_template("profile.html", error=e,useri=User,req=Userapp)
        else:
            return redirect("/")
    return redirect("/")

@app.route("/signin", methods = ['GET', 'POST'])
def signin():
    if request.method == 'POST':
        phone = request.form.get('phone')
        print(f"\n\n\n\n\n\n {phone} \n\n\n\n\n\n\n\n\n")

        User = user.query.filter_by(phone=phone).first()

        
        if User:
            print("\n\n\n\n\n\n\nhere mybe\n\n\n\n\n\n")
            session['user']=User.name
            session['phoneU']=User.phone
            print("\n\n\n\n\n\n herer \n\n\n\n\n\n\n\n\n")
            return redirect('/')
        else:
            print("\n\n\n\n\n\n wrong \n\n\n\n\n\n\n\n\n")

            return render_template('login.html', error_message="Incorrect phone")
    
    return render_template('login.html')

@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        phone = request.form.get('phone')
        otp = str(randint(1000,9999))
        token = f"user{uuid4()}"
        entry = user(name=name, phone=phone,otp=otp,token=token, date= datetime.now(),img='first.png')
        db.session.add(entry)
        db.session.commit()
         # Use the 'client' object to send an SMS
        message = client.messages.create(
                    from_='+16562186499',
                    body='hello here is your OTP: ' + otp,
                    to=f'+91{phone}'
                )
        return redirect('/verify')
    return render_template('register.html')

@app.route("/emp", methods = ['GET', 'POST'])
def Emp():
    # if 'phoneE' in session:
    #     return redirect("/empindex")
    if request.method == 'POST':
        phone = request.form.get('phone')
        try:
            checkemp = emp.query.filter_by(phone=phone).first()
        except Exception as e:
            print(f"\n\n\n\n\n\n error checkemp: {e} \n\n\n\n\n\n")
        
        t = str(uuid4())
        if checkemp:
            session['phoneE']=checkemp.phone
            checkemp.date = datetime.now()
            db.session.commit()
            # mke sms msg
                        
            # return redirect('/verify')       
            return redirect("/empindex")
        else:
            # Password does not match
            return render_template('login.html', error_message="Incorrect phone")
    
    return render_template('emplogin.html')

@app.route("/verify", methods = ['GET', 'POST'])
def verify():
    if(request.method=='POST'):
        '''Add entry to the database'''
        token = request.form.get('token')
        # checkT = emp.query.filter_by(token=token).first()
        User = user.query.filter_by(otp=token).first()

        # if (checkT):
        #     session['userE'] = checkT.name
        #     return redirect("/")
        if User:
            session['user'] = User.name
            session['phoneU'] = User.phone

            return redirect("/")
        else:
            return render_template('login.html', error_message="Incorrect phone")



    return render_template('verify.html')

@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop('user', None)  # Remove 'user' from the session
    if 'phoneE' in session:
        session.pop('userE', None)  # Remove 'userE' from the session
    return redirect('/signin')

app.run(debug=True)


