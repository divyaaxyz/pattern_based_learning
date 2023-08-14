from flask import Flask, render_template, request, redirect, session, jsonify
import smtplib
import random
import mysql.connector
import os

app=Flask(__name__)
app.secret_key=os.urandom(24)

conn=mysql.connector.connect(host="localhost",user="root", password="", database="hit2")
cursor=conn.cursor()

#below 3 lines are the code for creating table in the database
# if anytime a new table is required just remove these codes from the comments and execute the code i.e. app.py once
# after successful execution the table gets created in the database, and again make these 3 lines of codes in commentc 

# cursor.execute("DROP TABLE users")
# cursor.execute("DROP TABLE user")
# cursor.execute("CREATE TABLE user(user_id INTEGER PRIMARY KEY AUTO_INCREMENT, name VARCHAR(255) NOT NULL, email VARCHAR(255) UNIQUE, password VARCHAR(255) NOT NULL, score INTEGER)") 

#globally declaring these variables as they will be use in multiple functions
user_email=''
user_score=None
otp=''

# function for loading the login page
@app.route('/')
def login():
    return render_template('login.html')

#function for loading the signup page if the user is a new user
@app.route('/signup')
def register():
     return render_template('signup.html')

# function for directing the user to the home page after successful login
@app.route('/home')
def home_page():
     if 'user_id' in session:
          return render_template('home.html')
     else:
          return redirect('/')

# function for loading the page for getting the email for sending otp for new users   
@app.route('/user_email_validation')
def user_email_validation():
     return render_template('email_verification.html')

#function for loading the otp page
@app.route('/otp_get')
def otp_verify():
     return render_template('otp.html')

# function for verifying the login details of the already registered user
@app.route('/login_validation', methods=['POST'])
def login_validation():
     email=request.form.get('email')
     global user_email
     global user_score
     user_email= email
     password=request.form.get('password')
     cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""". format(email,password))
     users=cursor.fetchall()
     user_score=users[0][4]
     # cursor.execute("""UPDATE user SET score= 5 WHERE email LIKE '{email}'""")
     conn.commit()
     # users=cursor.fetchall()
     if len(users)>0:
          session['user_id']=users[0][0]
          return redirect('/home')
          # cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""". format(user_email))
          # user=cursor.fetchall()
          

          # return user_email
     else:

          # cursor.execute("""UPDATE user SET score= '{}' WHERE email LIKE '{}'""".format('4',user_email))
          # conn.commit()
          return redirect('/')
     

# function for sending the otp on email entered by the user on user_email_validation function
@app.route('/email_verification', methods=['POST'])
def email_send():
    global user_email
    email = request.form.get('email12') 
    user_email=email
    global otp
     
    try:
        if not email:
            raise ValueError("Email not provided")  # Raise an exception if email is empty

        otp = ''.join([str(random.randint(0, 9)) for i in range(6)])
        subject = 'Registration OTP'
        message = f'Your OTP for registration: {otp}'

       
        email_text = f"Subject: {subject}\n\n{message}"

        server = smtplib.SMTP('smtp.gmail.com', 587) 
        server.starttls()
        server.login('bariaqdus@gmail.com', 'hkcrlkqlycivdhwr')
        server.sendmail('bariaqdus@gmail.com', email, email_text)
        server.quit()

    except smtplib.SMTPException as e:
        # Handle SMTP-related errors
        print(f"SMTP Exception: {e}")
        return render_template('error.html')

    except Exception as e:
        # Handle other errors
        print(f"Failed to send email: {e}")
        return render_template('error.html')
     
    return redirect('/otp_get')


# function for verifying the otp enetered by the user on the otp.html page
@app.route('/otp_verification', methods=['POST'])
def otp_verification():
     # email=request.form.get('email12')
     score1=0
     global user_email
     global otp
     otp_get=request.form.get('OTP')
     if otp==otp_get:
          cursor.execute("""INSERT INTO `user` (`email`,`score`) VALUES ('{}', '{}')""".format(user_email, score1))
          conn.commit()
          return render_template('signup.html')
     else:
          return redirect('/otp_verification')




#function for adding new user's data into the database
@app.route('/add_user', methods=['POST'])
def add_user():
     global user_email
     # global user_score
     name=request.form.get('name1')
     # global user_email
     # email=user_email
     # email=request.form.get('email1')
     password=request.form.get('password1')
     # score1=0
     # cursor.execute("""INSERT INTO `user` (`user_id`, `name`, `password`) VALUES (NULL, '{}', '{}')""".format(name, password))
     cursor.execute("""UPDATE user SET name= '{}', password='{}' WHERE email LIKE '{}'""".format(name, password, user_email))
     conn.commit()

     cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""". format(user_email))
     user=cursor.fetchall()
     session['user_id']=user[0][0]
     # user_score=user[0][4]
     return redirect('/')


# function for storing the user's score after successful completion of the quiz
@app.route('/store_data', methods=['POST', 'GET'])
def store_data():
   
   global user_score
   data = request.get_json()
   calculated_data = int(data.get('data'))
#    calculated_data = data.get('data')
   user_score= calculated_data
   conn = mysql.connector.connect(host="localhost", user="root", password="", database="hit2")
   cursor=conn.cursor()
#    global user_email
   """cursor.execute("SELECT * FROM user")
   data=cursor.fetchall()
   user_identify=session['user_id']"""
    
    
    # Make sure you have established the database connection before executing any queries.
    # conn = get_db_connection()
   
   try:
     cursor.execute("""UPDATE user SET score= '{}' WHERE email LIKE '{}'""".format(calculated_data,user_email))
     conn.commit()
     # cursor.close()
     # cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""". format(user_email))
        # conn.commit()
     # user=cursor.fetchall()
     # user_score=[user[0][4]]

     return jsonify({'message': 'Data stored successfully'})
   
   except Exception as e:
     return jsonify({'error': str(e)})


# function for logging out the user from the web application
@app.route('/logout')
def logout():
     session.pop('user_id')
     return redirect('/')

# function for loading the webpage containing all the punjabi language levels
@app.route('/punjabi_levels')
def pun_levels():
     if 'user_id' in session:
          return render_template('punjabi_levels.html')
     else:
          return redirect('/')

# function for showing alert message if the user tries to play the next level before clearning the previous level
@app.route('/popup')
def popuplevel():
     if 'user_id' in session:
          return render_template('popup.html')
     else:
          return redirect('/')
     
@app.route('/pun_level1')
def pun_levels1():
     if 'user_id' in session:
          
          return render_template('pun_level1.html')
     else:
          return redirect('/')

@app.route('/pun_level2')
def pun_levels2():
     if 'user_id' in session:
        global user_email
        global user_score
        
     #    return user_score
        if user_score>=70:
           return render_template('pun_level2.html')
        else:
          return redirect('/popup')
     else:
          return redirect('/')  

@app.route('/pun_level3')
def pun_levels3():
     if 'user_id' in session:
        global user_email
        cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""". format(user_email))
        user=cursor.fetchall()
        quiz_score=user[0][4]
        if quiz_score>=70:
          return render_template('pun_level3.html')
        else:
          return redirect('/popup')
     else:
          return redirect('/') 
    

@app.route('/pun_level4')
def pun_levels4():
     global user_email
     cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""". format(user_email))
     user=cursor.fetchall()
     quiz_score=user[0][4]
     if 'user_id' in session:
          if quiz_score>=70:
             return render_template('pun_level4.html')
          else:
               return redirect('/popup')
     else:
          return redirect('/') 
     

@app.route('/pun_level5')
def pun_levels5():
     if 'user_id' in session:
        global user_email
        cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""". format(user_email))
        user=cursor.fetchall()
        quiz_score=user[0][4]
        if quiz_score>=70:
           return render_template('pun_level5.html')
        else:
          return redirect('/popup')
     else:
          return redirect('/') 
     

@app.route('/pun_level6')
def pun_levels6():
     global user_email
     cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""". format(user_email))
     user=cursor.fetchall()
     quiz_score=user[0][4]
     if 'user_id' in session:
          if quiz_score>=70:
             return render_template('pun_level6.html')
          else:
               return redirect('/')
     else:
          return redirect('/') 
     

@app.route('/pun_level7')
def pun_levels7():
     global user_email
     cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""". format(user_email))
     user=cursor.fetchall()
     quiz_score=user[0][4]
     if 'user_id' in session:
          if quiz_score>=70:
             return render_template('pun_level7.html')
          else:
               return redirect('/')
     else:
          return redirect('/') 
     

@app.route('/pun_level8')
def pun_levels8():
     global user_email
     cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""". format(user_email))
     user=cursor.fetchall()
     quiz_score=user[0][4]
     if 'user_id' in session:
          if quiz_score>=70:
             return render_template('pun_level8.html')
          else:
               return redirect('/')
     else:
          return redirect('/') 
     

@app.route('/pun_level9')
def pun_levels9():
     global user_email
     cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""". format(user_email))
     user=cursor.fetchall()
     quiz_score=user[0][4]
     if 'user_id' in session:
          if quiz_score>=70:
             return render_template('pun_level9.html')
          else:
               return redirect('/')
     else:
          return redirect('/') 

@app.route('/pun_level10')
def pun_levels10():
     global user_email
     cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""". format(user_email))
     user=cursor.fetchall()
     quiz_score=user[0][4]
     if 'user_id' in session:
          if quiz_score>=70:
             return render_template('pun_level10.html')
          else:
               return redirect('/')
     else:
          return redirect('/') 
                                

@app.route('/pun_quiz1')
def pun_quiz1():
     if 'user_id' in session:
          return render_template('pun_quiz1.html')
     else:
          return redirect('/')
     
@app.route('/pun_quiz2')
def pun_quiz2():
     if 'user_id' in session:
          return render_template('pun_quiz2.html')
     else:
          return redirect('/')

@app.route('/pun_quiz3')
def pun_quiz3():
     if 'user_id' in session:
          return render_template('pun_quiz3.html')
     else:
          return redirect('/')
     
@app.route('/pun_quiz4')
def pun_quiz4():
     if 'user_id' in session:
          return render_template('pun_quiz4.html')
     else:
          return redirect('/')

@app.route('/pun_quiz5')
def pun_quiz5():
     if 'user_id' in session:
          return render_template('pun_quiz5.html')
     else:
          return redirect('/')

@app.route('/pun_quiz6')
def pun_quiz6():
     if 'user_id' in session:
          return render_template('pun_quiz6.html')
     else:
          return redirect('/')

@app.route('/pun_quiz7')
def pun_quiz7():
     if 'user_id' in session:
          return render_template('pun_quiz7.html')
     else:
          return redirect('/')

@app.route('/pun_quiz8')
def pun_quiz8():
     if 'user_id' in session:
          return render_template('pun_quiz8.html')
     else:
          return redirect('/')

@app.route('/pun_quiz9')
def pun_quiz9():
     if 'user_id' in session:
          return render_template('pun_quiz9.html')
     else:
          return redirect('/')

@app.route('/pun_quiz10')
def pun_quiz10():
     if 'user_id' in session:
          return render_template('pun_quiz10.html')
     else:
          return redirect('/')
                                         
                    

@app.route('/malyalam_levels')
def malyalam_levels():
     return render_template('malyalam_levels.html')


@app.route('/telugu_levels')
def tamil_levels():
     return render_template('tamil_levels.html')


@app.route('/gujarati_levels')
def gujarati_levels():
     return render_template('gujarati_levels.html')


if __name__=="__main__":
      app.run(debug=True)