from journal import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json


@app.route("/api/entry", methods=["POST", "GET", "PATCH", "DELETE" ])
def journal_entry():
    conn = None
    cursor = None
    entry_fail = {
        "message" : "failed to post entry"
    }
    content_error = {
            "message" : "Length of entry error"
        }
    if request.method == "POST":
        data = request.json
        user_token = data.get("loginToken")
        user_entry = data.get("content")
    try:
        if (len(user_token) == 32):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id from user_session WHERE login_token=?",[user_token,])
            user_id = cursor.fetchone()
        #checking if user is logged in. if so, allow them to create a tweet
            if (len(user_entry) <= 400 and len(user_entry) > 0):
                cursor.execute("INSERT INTO entry(user_id, content) VALUES (?,?)",[user_id[0], user_entry])
                conn.commit()
                cursor.execute("SELECT id FROM entry WHERE content=?",[user_entry,])
                entryID = cursor.fetchone()
                cursor.execute("SELECT * FROM entry WHERE id=?",[entryID[0],])
                entry_info = cursor.fetchone()
                entry_resp = {
                "entryId" : entry_info[0],
                "userId" : entry_info[1],
                "content" : entry_info[2],
                "timeStamp" : entry_info[3]
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