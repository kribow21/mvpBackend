from journal import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
import datetime
import re

@app.route("/api/entry", methods=["POST", "GET", "DELETE" ])
def journal_entry():
    conn = None
    cursor = None
    entry_fail = {
        "message" : "failed to post entry"
    }
    content_error = {
            "message" : "Length of entry error"
        }
    date_wrong = {
                "message" : "Enter in correct format"
                }
    if request.method == "POST":
        data = request.json
        user_token = data.get("loginToken")
        user_entry = data.get("content")
        entry_date = data.get("date")
        date_pattern = "^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]{3})?(Z)?$"
        if(re.search(date_pattern, entry_date) == None):
            return Response(json.dumps(date_wrong, default=str),
                                mimetype='application/json',
                                status=400)
    try:
        if (len(user_token) == 32):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id from user_session WHERE login_token=?",[user_token,])
            user_id = cursor.fetchone()
        #checking if user is logged in. if so, allow them to create a tweet
            if (len(user_entry) <= 1000 and len(user_entry) > 0):
                cursor.execute("INSERT INTO entry(user_id, content, date_stamp) VALUES (?,?,?)",[user_id[0], user_entry, entry_date])
                conn.commit()
                cursor.execute("SELECT id FROM entry WHERE content=?",[user_entry,])
                entryID = cursor.fetchone()
                cursor.execute("SELECT * FROM entry WHERE id=?",[entryID[0],])
                entry_info = cursor.fetchone()
                entry_resp = {
                "entryId" : entry_info[0],
                "userId" : entry_info[1],
                "content" : entry_info[2],
                "dateStamp" : entry_info[3]
                }
                return Response(json.dumps(entry_resp, default=str),
                            mimetype='application/json',
                            status=201)
            else:
                return Response(json.dumps(content_error,default=str),
                                mimetype='application/json',
                                status=400)
        else:
            return Response(json.dumps(entry_fail,default=str),
                                mimetype='application/json',
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

    if request.method == "GET":
        params = request.args
    try:
        if(len(params) == 1):
            clientID = params.get("userId")
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entry WHERE user_id=? AND date_stamp > now() - INTERVAL 7 day",[clientID,])
            entry_info = cursor.fetchall()
            entry_list = []
            for entry in entry_info:
                a_entry = {
                "entryId" : entry[0],
                "userId" : entry[1],
                "content" : entry[2],
                "dateStamp" : entry[3]
                }
                entry_list.append(a_entry)
            return Response(json.dumps(entry_list, default=str),
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
        user_token = data.get("loginToken")
        entry_ID = data.get("entryId")
        confirm = {
            "message" : "entry deleted"
        }
        data_error = {
            "message" : "something wrong with passed data"
        }
        if (len(user_token) == 32 and isinstance(entry_ID, int) == True):
            try:
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM user_session WHERE login_token=?",[user_token,])
                session_userID = cursor.fetchone()
                cursor.execute("DELETE from entry WHERE id=? AND user_id=?",[entry_ID, session_userID[0]])
                conn.commit()
                return Response(json.dumps(confirm, default=str),
                                        mimetype="application/json",
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
        else:
            return Response(json.dumps(data_error, default=str),
                                mimetype='application/json',
                                status=401)
