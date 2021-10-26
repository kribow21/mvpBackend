from journal import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
import datetime
import re
from uuid import uuid4

@app.route("/api/editors", methods=["POST", "PATCH", "DELETE" ])
def journal_editor():
    conn = None
    cursor = None
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
    if request.method == "POST":
        data = request.json
        editor_email = data.get("email")          
        editor_password = data.get("password")
        if (editor_email == ''):
            return Response(json.dumps(if_empty, default=str),
                    mimetype='application/json',
                    status=409)
        elif (len(editor_password) > 21 or len(editor_password) < 1):
            return Response(json.dumps(len_error,default=str),
                            mimetype='application/json',
                            status=409)
        #used regular expression to match the passed email to the pattern above
        if(re.search(pattern, editor_email) == None):
            return Response(json.dumps(invalid_email,default=str),
                            mimetype='application/json',
                            status=409)
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO editor(email, password) VALUES (?,?)",[editor_email,editor_password]) 
        #in order to send back a token you need to create a token in the data editor_session table created with the selected id 
            cursor.execute("SELECT id FROM editor WHERE email=? AND password=?",[editor_email, editor_password,])
            editorID = cursor.fetchone()
            edit_token = uuid4().hex
            cursor.execute("INSERT INTO editor_session(editor_id, editor_token) VALUES (?, ?)",[editorID[0],edit_token])
            conn.commit()
            cursor.execute("SELECT * FROM editor_session WHERE editor_id=?",[editorID[0],])
            editor_info = cursor.fetchone()
            login_resp = {
                "editorId" : editor_info[0],
                "editorToken" : editor_info[1]
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
    elif request.method == "PATCH":
        data = request.json
        edit_email = data.get("email")          
        edit_password = data.get("password")
        edit_token = data.get("editorToken")
        edit_keys = data.keys()
        patch_fail = {
            "message" : "failed to match the login token to a editor"
        }
        if(edit_email != None):
            if(re.search(pattern, edit_email) == None):
                return Response(json.dumps(invalid_email,default=str),
                                mimetype='application/json',
                                status=400)
            if (edit_password != None and len(edit_password) > 21):
                return Response(json.dumps(len_error),
                            mimetype='application/json',
                            status=400)
        try:
            if (len(edit_token) == 32):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                #from the token grab the editorid to then make changes to the editors info
                cursor.execute("SELECT editor_id FROM editor_session WHERE editor_token=?",[edit_token,])
                varified_editor = cursor.fetchone()
                if (len(varified_editor) == 1):
                    try:
                        if "email" in edit_keys:
                            cursor.execute("UPDATE editor set email=? WHERE id=?",[edit_email, varified_editor[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email FROM editor WHERE id=?",[varified_editor[0],])
                            editors_info = cursor.fetchone()
                        if "password" in edit_keys:
                            cursor.execute("UPDATE editor set password=? WHERE id=?",[edit_password, varified_editor[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email FROM editor WHERE id=?",[varified_editor[0],])
                            editors_info = cursor.fetchone()
                    finally:
                            a_user = {
                                "editorId" : editors_info[0],
                                "email" : editors_info[1],
                            }
                            return Response(json.dumps(a_user, default=str),
                                                    mimetype='application/json',
                                                    status=200)
            else:
                return Response(json.dumps(patch_fail, default=str),
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
    elif request.method == "DELETE":
        data = request.json
        editor_pass = data.get("password")
        editor_token = data.get("editorToken")
        sucess_del = {
            "message" : "editor now deleted"
        }
        fail_del = {
            "message" : "something went wrong with deleteing the editor"
        }
        #checking passed data 
        if (len(editor_pass) > 21 or len(editor_pass) < 1):
                return Response(json.dumps(if_empty),
                                mimetype='application/json',
                                status=400)
        if (len(editor_token) != 32):
            return Response(json.dumps(fail_del),
                                mimetype='application/json',
                                status=400)
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT editor_token FROM editor_session WHERE editor_token=?",[editor_token,])
            valid_token = cursor.fetchone()
            if(len(valid_token) != 1):
                    return Response(json.dumps(fail_del, default=str),
                                mimetype="application/json",
                                status=401)
            cursor.execute("SELECT password FROM editor WHERE password=?",[editor_pass,])
            valid_pass = cursor.fetchone()
            if(valid_pass == None):
                    return Response(json.dumps(fail_del, default=str),
                                mimetype="application/json",
                                status=401)
            #first checks if the token is in the db, then id the password is in the db and if they are and match then they have the permission to delete the editor
            if (valid_token[0] == editor_token and valid_pass[0] == editor_pass):
                cursor.execute("DELETE FROM editor_session WHERE editor_token=?",[valid_token[0]])
                cursor.execute("DELETE FROM editor WHERE password=?",[editor_pass,])
                conn.commit()
                if (cursor.rowcount == 1):
                    return Response(json.dumps(sucess_del, default=str),
                                                mimetype='application/json',
                                                status=200)
                else:
                    return Response(json.dumps(fail_del, default=str),
                                                mimetype="application/json",
                                                status=400)
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