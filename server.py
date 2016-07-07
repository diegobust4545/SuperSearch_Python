from flask import Flask, render_template, request, redirect, url_for, session
import hashlib, uuid
import utils
import os
import psycopg2
import psycopg2.extras

import sys
reload(sys)
sys.setdefaultencoding("UTF8")

app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')

def connectToDB():
    connectionString = 'dbname=[INSERT DB] user=[INSERT USER] password=[INSERT PASSWORD] host=localhost'
    print connectionString
    try:
        return psycopg2.connect(connectionString)
    except:
        print("Can't Connect to the Database")


currentUser = ''

@app.route('/', methods=['GET', 'POST'])
def mainIndex():
    con = connectToDB()
    cur = con.cursor()
    # global currentUser
    if 'username' in session:
        currentUser = session['username']
    else:
        currentUser = ''
    queryType = 'None'
    rows = []
    # if user typed in a post ...
    if 'username' in session:
        print("Current User")
        print(currentUser)
        cur.execute("SELECT zipcode FROM users WHERE username = '%s'" % (currentUser))
        print("Zipcode")
        zipcode = cur.fetchone()
        print(zipcode[0])
        if request.method == 'POST':
            searchTerm = request.form['search']
            
            if searchTerm == 'movies':
                cur.execute("SELECT * from movies WHERE zip = %d" % (zipcode[0]))
                queryType = 'movies'
                rows = cur.fetchall()
            
            elif searchTerm != '':
                queryType = 'stores'
                query = "SELECT * FROM stores where (name LIKE %s OR type LIKE %s) and zip = %s"
                cur.execute(query, (searchTerm,searchTerm,zipcode[0],))
                rows = cur.fetchall()
                if rows == []:
                    queryType = 'movies'
                    query = "SELECT * FROM movies where movie LIKE %s AND zip = %s"
                    cur.execute(query, (searchTerm,zipcode[0],))
                    rows = cur.fetchall()
                if rows == []:
                    cur.execute("SELECT * FROM stores where type LIKE %s and zip = %s" % (searchTerm,zipcode[0],))
                    rows = cur.fetchall()
                if rows == []:
                    cur.execute("SELECT * FROM stores where name LIKE %s and zip = %s" % (searchTerm,zipcode[0],))
                    rows = cur.fetchall()
                if rows == []:
                    queryType = ''
                    # TODO: write code...
                
    else:
         if request.method == 'POST':
            searchTerm = request.form['search']
            if searchTerm == 'movies':
                cur.execute("SELECT * from movies")
                queryType = 'movies'
                rows = cur.fetchall()

            
            elif searchTerm != '':
                queryType = 'stores'
                print("Testing P: ")
                print(searchTerm)
                queryType = 'stores'
                query = "SELECT * FROM stores where (name LIKE %s OR type LIKE %s)"
                cur.execute(query, (searchTerm,searchTerm,))
                rows = cur.fetchall()
                print(rows)
                if rows == []:
                    queryType = 'movies'
                    query = "SELECT * FROM movies where movie LIKE %s"
                    cur.execute(query, (searchTerm,))
                    rows = cur.fetchall()
                if rows == []:
                    cur.execute("SELECT * FROM stores where name LIKE '%%%s%%' OR type LIKE '%%%s%%'" % (searchTerm,searchTerm,))
                    rows = cur.fetchall()
                # rows = cur.fetchall()
                print("HERE: ")
                print(rows)
                if rows == []:
                    queryType = ''
            # con.commit()
    return render_template('index.html', queryType=queryType, results=rows, selectedMenu='Home', user = currentUser)

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    con = connectToDB()
    cur = con.cursor()
    statement = ''
    currentUser = ''
    # if user typed in a post ...
    if request.method == 'POST':
        session['username'] = request.form['username']
        pw = request.form['pw']
        query = "select * from users WHERE username = '%s' AND password = '%s'" % (currentUser, pw)
        print query
        cur.execute(query)
          
        if cur.fetchone():
            return redirect(url_for('mainIndex'))
         
    if 'username' in session:
        currentUser = session['username']
    else:
        currentUser = ''
    return render_template('login.html', selectedMenu='Login', user = currentUser, statement = statement)
    

@app.route('/newUser', methods=['GET', 'POST'])
def newUser():
    if 'username' in session:
        currentUser = session['username']
    else:
        currentUser = ''
    
    con = connectToDB()
    cur = con.cursor()
    # if user typed in a post ...
    if request.method == 'POST':
        # http://stackoverflow.com/questions/9594125/salt-and-hash-a-password-in-python
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(request.form['password'] + salt).hexdigest()
        cur.execute("""INSERT INTO users (username, password, zipcode) VALUES (%s, %s, %s)""" ,(request.form['username'],hashed_password ,request.form['zipcode']))
        con.commit()
        print("Great Success!")
    return render_template('newUser.html')



if __name__ == '__main__':
    app.debug=True
    app.run(host='0.0.0.0', port=8080)
