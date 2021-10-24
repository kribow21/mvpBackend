from journal import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
import datetime
import re
from uuid import uuid4

@app.route("/api/users", methods=["POST", "PATCH", "DELETE" ])
def journal_user():
    conn = None
    cursor = None
    if request.method == "POST":
        data = request.json
        user_email = data.get("email")          
        user_password = data.get("password")
        first_name = data.get("firstName")
        if_empty = {
            "message" : "Enter in required data"
        }
        invalid_email = {
                "messgae" : "please use a valid email"
                        }
        pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
        len_error = {
            "message" : "Length of input exceeds limit"
        }
        if (user_email == ''):
            return Response(json.dumps(if_empty, default=str),
                    mimetype='application/json',
                    status=409)
        elif (len(first_name) > 31 or len(first_name) < 1):
            return Response(json.dumps(len_error, default=str),
                            mimetype='application/json',
                            status=409)
        elif (len(user_password) > 21 or len(user_password) < 1):
            return Response(json.dumps(len_error,default=str),
                            mimetype='application/json',
                            status=409)
        #used regular expression to match the passed email to the pattern above
        if(re.search(pattern, user_email) == None):
            return Response(json.dumps(invalid_email,default=str),
                            mimetype='application/json',
                            status=409)
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(email, password, first_name) VALUES (?,?,?)",[user_email,user_password, first_name]) 
        #in order to send back a token you need to create a token in the data user_session table created with the selected id 
            cursor.execute("SELECT id FROM user WHERE email=? AND password=?",[user_email, user_password,])
            userID = cursor.fetchone()
            tokenID = uuid4().hex
            cursor.execute("INSERT INTO user_session(login_token, user_id) VALUES (?, ?)",[tokenID, userID[0],])
            conn.commit()
            cursor.execute("SELECT user.first_name, user_session.login_token FROM user_session INNER JOIN user ON user_session.user_id=user.id WHERE id=?",[userID[0],])
            user_info = cursor.fetchone()
            login_resp = {
                "firstName" : user_info[0],
                "loginToken" : user_info[1]
            }
            return Response(json.dumps(login_resp, default=str),
                            mimetype='application/json',
                            status=201)
        except mariadb.DatabaseError:
            print('Something went wrong with connecting to database')
        except mariadb.DataError: 
            print('Something went wrong with your data')
        except mariadb.OperationalError:
            print('Something wrong with the connection')
        except mariadb.ProgrammingError:
            print('Your query was wrong')
        except mariadb.IntegrityError:
            print('Your query would have broken the database and we stopped it')
        except mariadb.InterfaceError:
            print('Something wrong with database interface')
        except:
            print('Something went wrong')
        finally:
            if(cursor != None):
                cursor.close()
                print('cursor closed')
            else:
                print('no cursor to begin with')
            if(conn != None):   
                conn.rollback()
                conn.close()
                print('connection closed')
            else:
                print('the connection never opened, nothing to close')