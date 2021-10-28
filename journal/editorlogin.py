from journal import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
import datetime
from uuid import uuid4
import re
import bcrypt


@app.route("/api/editorlogin", methods=["POST", "DELETE"])
def editorlogin():
    conn = None
    cursor = None
    pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"

    if request.method == "POST":
        data = request.json
        editor_email = data.get("email")
        editor_pass = data.get("password")
        if_empty = {
            "message" : "Enter in required data"
        }
        invalid_email = {
            "messgae" : "please use a valid email"
                    }
        fail_login = {
            "message" : "Failed to login"
        }
    #checks if things are empty or not correct email format before opening db
        if (editor_email == ''):
            return Response(json.dumps(if_empty),
                                mimetype='application/json',
                                status=400)
        elif(re.search(pattern, editor_email) == None):
            return Response(json.dumps(invalid_email,default=str),
                                mimetype='application/json',
                                status=400)
        elif (editor_pass == ''):
            return Response(json.dumps(if_empty),
                                mimetype='application/json',
                                status=400)
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT password,id from editor WHERE email=?",[editor_email,])
            editor_info = cursor.fetchone()
        #accounts for if password does not match or email does not match. the elif if it does match
            if(editor_info == None):
                    return Response(json.dumps(fail_login, default=str),
                                            mimetype='application/json',
                                            status=401)
            #if editorid's correspond then create/insert a token for their session
            elif (bcrypt.checkpw(editor_pass.encode(),editor_info[0].encode())):
                tokenID = uuid4().hex
                cursor.execute("INSERT INTO editor_session (editor_token,editor_id) VALUES (?,?)",[tokenID,editor_info[1]])
                conn.commit()
            else:
                return Response(json.dumps(fail_login, default=str),
                                            mimetype='application/json',
                                            status=401)
            if (editor_info != None):
                cursor.execute("SELECT * FROM editor_session WHERE editor_id=?",[editor_info[1],])
                select_editor = cursor.fetchone()
                a_editor = {
                    "editorId" : select_editor[0],
                    "editorToken" : select_editor[1],
                }
                return Response(json.dumps(a_editor, default=str),
                                            mimetype='application/json',
                                            status=200)
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

    if request.method == "DELETE":
        data = request.json
        edit_token = data.get("editorToken")
        invalid = {
            "message" : "invalid token"
        }
        confirm = {
            "message" : "valid token, deleted"
        }
        try:
            if (len(edit_token) == 32):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM edit_session WHERE editor_token=?",[edit_token,])
                conn.commit()
                if (cursor.rowcount ==1):
                    return Response(json.dumps(confirm, default=str),
                                    mimetype="application/json",
                                    status=200)
            else:
                return Response(json.dumps(invalid, default=str),
                                mimetype="application/json",
                                status=401)
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