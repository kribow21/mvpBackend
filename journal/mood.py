from journal import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json
import datetime


@app.route("/api/mood", methods=["POST", "GET"])
def user_mood():
    conn = None
    cursor = None
    mood_fail = {
        "message" : "failed to post mood"
    }
    mood_sucess = {
        "message" : "mood posted"
    }
    mood_error = {
        "message" : "User daily mood post exceeds limit"
    }
    if request.method == "POST":
        data = request.json
        user_token = data.get("loginToken")
        mood_date = data.get("date")
        user_mood = data.get("mood")
        date_wrong = {
                "message" : "Enter in correct format"
                }
        try:
            #datetime is a module that has a class called datetime that has the proper format to check if the passed datetime match
            datetime.datetime.strptime(mood_date, '%Y-%m-%d')
        except ValueError:
            return Response(json.dumps(date_wrong, default=str),
                                mimetype='application/json',
                                status=409)
    try:
        if (len(user_token) == 32):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id from user_session WHERE login_token=?",[user_token,])
            user_id = cursor.fetchone()
            if(len(user_id) == 1):
                try:
                    cursor.execute("INSERT INTO mood(user_id,date,mood) VALUES (?,?,?)", [user_id[0],mood_date, user_mood])
                    conn.commit()
                    return Response(json.dumps(mood_sucess, default=str),
                                mimetype='application/json',
                                status=201)
                except mariadb.IntegrityError:
                    return Response(json.dumps(mood_error, default=str),
                                mimetype='application/json',
                                status=409)
            else:
                return Response(json.dumps(mood_fail, default=str),
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
                userID = params.get("userId")
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT date,mood FROM mood WHERE user_id=?",[userID,])
                allMoods = cursor.fetchall()
                print(allMoods)
                moods = {
                    
                }
                for mood in allMoods:
                    moods[mood[0].strftime('%Y-%m-%d')] = mood[1]
                return Response(json.dumps(moods, default=str),
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
