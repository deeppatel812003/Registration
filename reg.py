from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy 
import smtplib, ssl
import hashlib
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///registration.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

#database table and database
class registration_details(db.Model):
   id = db.Column('registration_id', db.Integer, primary_key = True)
   firstname = db.Column(db.String(30))
   lastname = db.Column(db.String(30))
   email = db.Column(db.String(30))
   password = db.Column(db.String(256))
   # confirmpassword = db.Column(db.String(256))
   address = db.Column(db.String(500))
   hobbies = db.Column(db.String(50))
   gender = db.Column(db.String(10))

   def __init__(self, firstname, lastname, email, password, confirmpassword, address, hobbies, gender):
      self.firstname = firstname
      self.lastname = lastname
      self.email = email
      self.password = password
      # self.confirmpassword = confirmpassword
      self.address = address
      self.hobbies = hobbies
      self.gender = gender

@app.route('/')
def show_all():
   return render_template('show_all.html' )



@app.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['firstname'] or not request.form['lastname'] or not request.form['email'] or not request.form['password'] or not request.form['confirmpassword'] or not request.form['address'] or not  request.form['hobbies'] or not request.form['gender']:
         flash('Please enter all the fields', 'error')
      else:
         hobby = request.form.getlist('hobbies')
         hby_csv = ','.join(hobby)
         
         
         #hashlib.md5 to password hash and encrypted
         password = request.form['password']
         hashpassword = hashlib.md5(password.encode('utf-8')).hexdigest()

         user = registration_details(request.form['firstname'], request.form['lastname'], request.form['email'], hashpassword, request.form['confirmpassword'], request.form['address'], hby_csv, request.form['gender'])
         # print("data:")
         # print(request.form['firstname'], request.form['lastname'], request.form['email'], hashpassword, request.form['confirmpassword'], request.form['address'], hby_csv, request.form['gender'])
         
         
         db.session.add(user)
         db.session.commit()
         sendemail()
         # get_joke()

         flash('Record was successfully added')
      return redirect(url_for('show_all'))
   return render_template('new.html')


def sendemail():
#for confirmation email sending
      port = 465  # For SSL
      smtp_server = "smtp.gmail.com"
      sender_email = "deeppatel849099@gmail.com"  # Enter your address
      receiver_email = request.form['email']  # Enter receiver address
      password = 'lkrcfzxqrfrkiosk'
      message = """Subject:Data Stored Successfully \n
      Recive your information
      """

      context = ssl.create_default_context()
      with smtplib.SMTP_SSL(smtp_server, port, context=context) as server: 
         server.login(sender_email, password)
         server.sendmail(sender_email, receiver_email, message)

#Create endpoint joke which fetches a joke from API 

@app.route('/joke', methods=['GET', 'POST'])
def get_joke():
        url = "https://icanhazdadjoke.com/"
        headers = {"Accept": "application/json"}
    
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                joke_data = response.json()
                joke = joke_data['joke']
                return render_template('Joke.html', joke=joke)
            else:
                flash("Failed to fetch a joke. Please try again later.", "error=error")
                return redirect('/')
        except requests.exceptions.RequestException as e:
            flash("Failed to fetch a joke: {e}", "error")
            return redirect('/')

    #create login page validation
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()

        user = registration_details.query.filter_by(email=email, password=password).first()

        if user:
            session['user_id'] = user.id
            flash('Logged in successfully', 'success')
            return redirect('/joke')
        else:
            flash('Invalid email or password', 'error')

    return render_template('show_all.html')


#logout from the joke page
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')  # Flash the success message
    return redirect(url_for('show_all'))



if __name__ == '__main__':
   with app.app_context():
    db.create_all()
   app.run(debug = True)

       