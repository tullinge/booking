from flask import Flask, redirect, url_for, request, render_template, template_rendered
import time

app = Flask(__name__, template_folder='.')

@app.route('/', methods = ['get','post'])
def students_login():
    return render_template('student_login.html')
#    if request.method == 'post':
#        return request.method['usercode']

if __name__ == '__main__':
    app.run(debug=True)

