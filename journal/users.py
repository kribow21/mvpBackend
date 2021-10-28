from journal import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
import datetime
import re
from uuid import uuid4
import bcrypt

@app.route("/api/users", methods=["POST", "PATCH", "DELETE" ])
def journal_user():
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
    salt = bcrypt.gensalt()
    if request.method == "POST":
        data = request.json
        user_email = data.get("email")          
        user_password = data.get("password")
        first_name = data.get("firstName")
        if (user_email == ''):
            return Response(json.dumps(if_empty, default=str),
                    mimetype='application/json',
                    status=409)
        elif (len(first_name) > 16 or len(first_name) < 1):
            return Response(json.dumps(len_error, default=str),
                            mimetype='application/json',
                            status=409)
        elif (len(user_password) < 1 or len(user_password) > 151):
            return Response(json.dumps(len_error,default=str),
                            mimetype='application/json',
                            status=409)
        #used regular expression to match the passed email to the pattern above
        if(re.search(pattern, user_email) == None):
            return Response(json.dumps(invalid_email,default=str),
                            mimetype='application/json',
                            status=409)
        hashed = bcrypt.hashpw(user_password.encode(), salt)
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(email, password, first_name) VALUES (?,?,?)",[user_email,hashed, first_name]) 
        #in order to send back a token you need to create a token in the data user_session table created with the selected id 
            cursor.execute("SELECT id FROM user WHERE email=? AND password=?",[user_email, hashed,])
            userID = cursor.fetchone()
            tokenID = uuid4().hex
            cursor.execute("INSERT INTO user_session(login_token, user_id) VALUES (?, ?)",[tokenID, userID[0],])
            conn.commit()
            cursor.execute("SELECT user.id, user.first_name, user_session.login_token FROM user_session INNER JOIN user ON user_session.user_id=user.id WHERE id=?",[userID[0],])
            user_info = cursor.fetchone()
            login_resp = {
                "userId" : user_info[0],
                "firstName" : user_info[1],
                "loginToken" : user_info[2]
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
        edit_name = data.get("firstName")
        edit_token = data.get("loginToken")
        edit_keys = data.keys()
        patch_fail = {
            "message" : "failed to match the login token to a user"
        }
        if(edit_email != None):
            if(re.search(pattern, edit_email) == None):
                return Response(json.dumps(invalid_email,default=str),
                                mimetype='application/json',
                                status=400)
            if (edit_password != None and len(edit_password) > 151):
                return Response(json.dumps(len_error),
                            mimetype='application/json',
                            status=400)
            if (edit_name != None and len(edit_name) > 16):
                return Response(json.dumps(len_error),
                            mimetype='application/json',
                            status=400)
        try:
            if (len(edit_token) == 32):
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                #from the token grab the userid to then make changes to the users info
                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[edit_token,])
                varified_user = cursor.fetchone()
                if (len(varified_user) == 1):
                    try:
                        if "email" in edit_keys:
                            cursor.execute("UPDATE user set email=? WHERE id=?",[edit_email, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, first_name FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                        if "password" in edit_keys:
                            hashedpass = bcrypt.hashpw(edit_password.encode(), salt)
                            cursor.execute("UPDATE user set password=? WHERE id=?",[hashedpass, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, first_name FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                        if "firstName" in edit_keys:
                            cursor.execute("UPDATE user set first_name=? WHERE id=?",[edit_name, varified_user[0]])
                            conn.commit()
                            cursor.execute("SELECT id, email, first_name FROM user WHERE id=?",[varified_user[0],])
                            user_info = cursor.fetchone()
                    finally:
                            a_user = {
                                "userId" : user_info[0],
                                "email" : user_info[1],
                                "firstName" : user_info[2],
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
        user_pass = data.get("password")
        user_token = data.get("loginToken")
        sucess_del = {
            "message" : "user now deleted"
        }
        fail_del = {
            "message" : "something went wrong with deleteing the user"
        }
        #checking passed data 
        if (len(user_pass) > 151 or len(user_pass) < 1):
                return Response(json.dumps(if_empty),
                                mimetype='application/json',
                                status=400)
        if (len(user_token) != 32):
            return Response(json.dumps(fail_del),
                                mimetype='application/json',
                                status=400)
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT login_token FROM user_session WHERE login_token=?",[user_token,])
            valid_token = cursor.fetchone()
            if(len(valid_token) != 1):
                    return Response(json.dumps(fail_del, default=str),
                                mimetype="application/json",
                                status=401)
            cursor.execute("SELECT user.password, user_session.user_id FROM user_session INNER JOIN user ON user_session.user_id=user.id WHERE login_token=?",[valid_token[0],])
            valid_info = cursor.fetchone()
            valid_pass = valid_info[0]
            if(valid_pass == None):
                    return Response(json.dumps(fail_del, default=str),
                                mimetype="application/json",
                                status=401)
            #first checks if the token is in the db,if they match then they have the permission to delete the user
            if (valid_token[0] == user_token):
                cursor.execute("DELETE FROM user_session WHERE login_token=?",[valid_token[0]])
                conn.commit()
            if(bcrypt.checkpw(user_pass.encode(), valid_pass.encode())):
                cursor.execute("DELETE FROM user WHERE password=?",[valid_pass,])
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