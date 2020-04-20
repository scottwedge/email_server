import requests
import smtplib
import re

from flask import Flask

# Firebase DB Info
users_url = "https://quickstart-1578522372773.firebaseio.com/users/.json"
user_url_base = "https://quickstart-1578522372773.firebaseio.com/users/"
workouts_url_base = "https://quickstart-1578522372773.firebaseio.com/workouts/"
workouts_performed_url_base = "https://quickstart-1578522372773.firebaseio.com/workouts_performed/"

# Gmail Info
sender = 'no.reply.gymdiligence@gmail.com'
mail = smtplib.SMTP('smtp.gmail.com', 587)
mail.ehlo()

app = Flask(__name__)

# login to server
mail.starttls()
mail.login(sender, 'Heyheyuu1')

# Email Helper Functions
def read_file_and_fill_template(file_path, user_info_dict):
    ''' open the file, scanning line by line, replacing each template string
        with the values from the user_info_dictionary '''
    content_string = ''
    
    with open(file_path) as f:
        for line in f.readlines():
            if '{' in line:
                the_word = re.search('{(.*)}',line).group(1)
                new_line = line.replace(the_word, user_info_dict[the_word])
                content_string += new_line
            else:
                content_string += line

    return content_string.replace('{','').replace('}','')

def send_email(receiver, content):
    print(f'\n---- Sending Email To: {receiver} ----')

    try:
        mail.sendmail(sender, receiver, content)
    except Exception as e:
        print(e)
        return
    
    print(f'\n---- Email Sent ----')

def get_receivers_info(receiver):
    ''' method reads the database (using receivers_email) and returns user info dictionary '''
    
    users_url = "https://quickstart-1578522372773.firebaseio.com/users/.json"
    
    # read the users db
    response = requests.get(users_url)

    if response.json():
        for username, user_info in response.json().items():
            if len(user_info) > 1:
                # using user email
                if user_info['email'] == receiver:
                    # return user info dictionary
                    return { 'username': username, 'password': user_info['password'] }
    return None

# Email API
@app.route('/')
def home():
    return 'LiftsKit - Automated Email Server'

@app.route('/send_confirmation_email/<string:receiver>/<string:username>/')
def send_confirmation_email(receiver, username):
    greeting_file_path = 'email_templates/greeting_template.txt'

    # fill the template and send the email
    content = read_file_and_fill_template(greeting_file_path, { 'username': username })
    send_email(receiver, content)
    return 'Confirmation Email Sent Successfully'

@app.route('/send_recovery_email/<string:receiver>/')
def send_email_recovery(receiver):
    email_recovery_file_path = 'email_templates/recovery_template.txt'
    
    # get the receivers info from the db
    user_info_dict = get_receivers_info(receiver)

    if user_info_dict:
        # fill the template and send the email
        email_content = read_file_and_fill_template(email_recovery_file_path, user_info_dict)
        send_email(receiver, email_content)
        return 'Password Recovery Email Sent Successfully'
    return 'Error - No User info Found in DB'


app.run(port=5000)