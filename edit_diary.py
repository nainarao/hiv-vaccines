__author__ = 'naina'

from flask import Flask, render_template, request
import sys
import time
from datetime import datetime
import dev_diary as dev_diary

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/editDiary', methods=['GET', 'POST'])
def editDiary():
    dev_diary.initialize_medidata()
    sub_key = request.form['key']
    dt = datetime.strptime(request.form['today'],'%Y-%m-%d')
    s = dt.strftime("%d %b %Y")
    tm = request.form['time']
    print tm
    dev_diary.updateSubjectDiary(sub_key, s, 1)
    print "TODAY DATE: ", request.form['today'], s
    sub_xml = dev_diary.printPatient(sub_key)
    return render_template('displaydiary.html', root=sub_xml)
    #return 'Hello have fun learning python <br/> <xmp> %s </xmp> <a href="/">Back Home</a>' % (str(sub_xml))

@app.route('/getSubject', methods=['POST'])
def getSubject():
    dev_diary.initialize_medidata()
    sub_key = request.form['key']
    dt = request.form['today']
    dt = datetime.strptime(dt,'%Y-%m-%d')
    s = dt.strftime("%d %b %Y")
    dev_diary.setSubjectDiary(sub_key, s)
    print "TODAY DATE: ", request.form['today'],
    sub_xml = dev_diary.printPatient(sub_key)
    return render_template('displaydiary.html', root=sub_xml)
    #return 'Hello have fun learning python <br/> <xmp> %s </xmp> <a href="/">Back Home</a>' % (str(sub_xml))

@app.route('/hello', methods=['POST'])
def hello():
    dev_diary.initialize_medidata()
    first_name = request.form['key']
    sub_xml = dev_diary.printPatient(first_name)
    print sub_xml
    #sub_xml = sub_xml.replace("\"", "\\""s")
    return render_template('displaydiary.html', root=sub_xml)
    #return 'Hello have fun learning python <br/> <xmp> %s </xmp> <a href="/">Back Home</a>' % (str(sub_xml))
