import asyncio
import flask
from flask_session import Session
import requests
from flask import flash, render_template, request, jsonify, session, redirect
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import psycopg2
import psycopg2.extras
import downloadUtilities

app = flask.Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.url_map.strict_slashes = False

subdomain = os.environ.get('SUBDOMAIN')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        if not session.get('email'):
            return render_template('index.html')
        else:
            if session.get('authorised') == True:
                return redirect('/mirror')
            return render_template('index.html')
    if request.method == 'POST':
        session['email'] = request.form.get('email')
        email = session['email']
        return redirect('/drive')

@app.route('/drive', methods=['GET'])
def drive():

    if not session.get('email'):
        return redirect('/')
    else:
        email = session['email']
        existing = requests.get(request.url_root + 'api/checkExisting?email=' + email).text
        if existing == 'Found':
            session['authorised'] = True
        else:
            session['authorised'] = None
        return render_template('gdrive.html')

@app.route('/auth', methods=['GET'])
def auth():
    authLink = requests.get(request.url_root + 'api/getAuthLink').json()
    return render_template('auth.html', authLink = authLink)

@app.route('/mirror', methods=['GET', 'POST'])
def mirror():
    if request.method == 'GET':
        if not session.get('email'):
            return redirect('/')
        else:
            email = session['email']
            if session.get('authorised') == True:
                return render_template('mirror.html')
            else:
                return redirect('/')
    if request.method == 'POST':
        email = session['email']
        urlLink = request.form.get('link')
        folderID = request.form.get('folderID')
        session['folderID'] = folderID
        if urlLink == '':
            flash('Please enter a valid URL')
            return redirect('/mirror')
        else:
            if folderID == '':
                folderID = 'root'
            downloadReq = requests.get('http://pellmirror.loca.lt/' + 'api/download?email=' + email + '&link=' + urlLink + '&folderID=' + folderID)
            if downloadReq.text == 'Added':
                flash('Added! Check Status')
            else:
                flash(downloadReq.text)
            return redirect('/mirror')
    session['_flashes'].clear()

@app.route('/status', methods=['GET', 'POST'])
def statusPage():
    if request.method == 'GET':
        if not session.get('email'):
            return redirect('/')
        else:
            email = session['email']
            statusJSON = requests.get('http://pellmirror.loca.lt/' + 'api/status?email=' + email).json()
            return render_template('status.html', statusJSON = statusJSON)
    if request.method == 'POST':
        email = session['email']
        if session.get('authorised') == True:
            statusJSON = requests.get('http://pellmirror.loca.lt/' + 'api/delete?email=' + email)
            return redirect('/mirror')

@app.route('/authorise', methods=['POST'])
def authorise():
    authCode = request.form.get('authCode')
    email = session['email']
    authorise = requests.get(request.url_root + 'api/recieveAuthLink?email=' + email + '&code=' + authCode).text
    if authorise == 'Success':
        session['authorised'] = True
        return redirect('/mirror')
    else:
        session['authorised'] = None
        return redirect('/')

@app.route('/logout', methods=['GET'])
def logout():
    if not session.get('email'):
        return redirect('/')
    else:
        session['email'] = None
        session['authorised'] = None
        return redirect('/')

@app.route('/api/getAuthLink', methods=['GET'])
def getAuthLink():
    gauth = GoogleAuth()           
    auth_url = gauth.GetAuthUrl()
    print(auth_url)
    return jsonify(auth_url)

@app.route('/api/checkExisting', methods=["GET"])
def checkExisting():
    if 'email' in request.args:
        email = request.args['email']
        dbURL = os.environ.get('DATABASE_URL')
        try:
            conn = psycopg2.connect(dbURL)
            print("Connected to DataBase")
            cur = conn.cursor()
            checkPrevious = """SELECT * FROM token WHERE email = %s"""
            cur.execute(checkPrevious, (email,))
            if cur.rowcount == 0:
                return "None"
            else:
                return "Found"
        except psycopg2.DatabaseError as e:
            print(e)

@app.route('/api/recieveAuthLink', methods=['GET'])
def recieveAuthLink():
    if 'code' and 'email' in request.args:
        authCode = request.args['code']
        email = request.args['email']
        print(authCode)
        gauth = GoogleAuth()
        gauth.Auth(authCode)
        print("SENDING TO DB NOW")
        sendTokenToDB(gauth.credentials.refresh_token, email)
        return 'Success', 200
    else:
        return 'Invalid Auth Code', 404

@app.route('/api/download', methods=['GET'])
def download():
    argList = list(request.args.keys())
    for param in argList:
        if param == 'email':
            email = request.args['email']
            continue
        elif param == 'link':
            link = request.args['link']
            continue
        elif param == 'folderID':
            if request.args['folderID'] != 'root':
                folderID = request.args['folderID']
            else:
                folderID = None
            continue
        else:
            link = link + "&" + param + "=" + request.args[param]
    if folderID is not None:
        response = downloadUtilities.downloadURL(link, email, folderID)
    else:
        response = downloadUtilities.downloadURL(link, email)
    response.downloadObject.update()
    if response.downloadObject.has_failed or response.failed == True:
        return response.downloadObject.error_message , 404
    else:
        return "Added", 200

@app.route('/api/status', methods=['GET'])
def status():
    if 'email' in request.args:
        email = request.args['email']
        resultJSON = downloadUtilities.genStatusJSON(email)
        return resultJSON, 200
    else:
        return 'Invalid', 404
        
@app.route('/api/statusShortcut', methods=['GET'])
def statusShortcut():
    if 'email' in request.args:
        email = request.args['email']
        resultJSON = downloadUtilities.genStatusShortcutJSON(email)
        return resultJSON, 200
    else:
        return 'Invalid', 404

@app.route('/api/delete', methods=['GET'])
def delete():
    if 'email' in request.args:
        email = request.args['email']
        result = downloadUtilities.deleteDownload(email)
        if result == True:
            return "Deleted", 200
        else:
            return "Failed", 404
    else:
        return 'Invalid', 404

def sendTokenToDB(token, email):
    dbURL = os.environ.get('DATABASE_URL')
    try:
        conn = psycopg2.connect(dbURL)
        print("Connected to DataBase")
        cur = conn.cursor()
        createTable = """CREATE TABLE IF NOT EXISTS token (
            email VARCHAR(255) NOT NULL PRIMARY KEY,
            refreshtoken VARCHAR(500) NOT NULL)"""
        cur.execute(createTable)
        conn.commit()
        checkPrevious = """SELECT * FROM token WHERE email = %s"""
        cur.execute(checkPrevious, (email,))
        if cur.rowcount == 0:
            insertToken = """INSERT INTO token (email, refreshtoken) VALUES (%s, %s)"""
            cur.execute(insertToken, (email, token))
            conn.commit()
        else:
            updateToken = """UPDATE token SET refreshtoken = %s WHERE email = %s"""
            cur.execute(updateToken, (token, email))
            conn.commit()
        print("Token Inserted")
        conn.close()
    except psycopg2.DatabaseError as e:
        print(e)

if __name__ == "__main__":
    app.debug = False
    app.run("0.0.0.0",port=5000,threaded=True)
