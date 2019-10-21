from flask import Flask, redirect, url_for, request, render_template, template_rendered
from flask_mysqldb import MySQL
import time

app = Flask(__name__, template_folder='.')

app.config['MYSQL_HOST'] = 'mysql683.loopia.se'
app.config['MYSQL_USER'] = 'Booking@s261825'
app.config['MYSQL_PASSWORD'] = 'Booking2019'
app.config['MYSQL_DB'] = 'swe3d_com'

letter_list = ["A", "B", "C", "D", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "V", "X", "Z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

def letter_check(x):
    for L in letter_list:
        if x != L:
            pass
        else:
            pass

@app.route('/', methods = ['get','post'])
def students_login():
    return render_template('student_login.html')
    if request.method == 'post':
        usercodePY = str(request.form['usercode'])
        if len(usercodePY) == 4:
            for n in usercodePY:
               letter = usercodePY[n]
               letter = letter.upper()
               letter_check(letter)


if __name__ == '__main__':
    app.run(debug=True)

