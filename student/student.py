from flask import Flask, redirect, url_for, request, render_template, template_rendered
from flask_mysqldb import MySQL
import time

app = Flask(__name__, template_folder='.')

app.config['MYSQL_HOST'] = 'mysql683.loopia.se'
app.config['MYSQL_USER'] = 'Booking@s261825'
app.config['MYSQL_PASSWORD'] = 'Booking2019'
app.config['MYSQL_DB'] = 'swe3d_com' 
 
mysql = MySQL(app)

character_list  = ['A', 'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'X', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def character_check(x):
    for L in character_list:
        if x != L:
            pass
        else:
            pass

@app.route('/student_login', methods = ['GET','POST'])
def students_login():
    if request.method == 'GET':
        return render_template('student_login.html')
    else:
        username =  request.form['usercode'].upper()
        if username == 'BEAR':
            return render_template('student_signup.html')
        else:
            pass



@app.route('/student_signup')
def student_signup():
    return render_template('student_signup.html')

if __name__ == '__main__':
    app.run(debug=True)

