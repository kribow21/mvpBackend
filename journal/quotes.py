from journal import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json

@app.route("/api/quotes", methods=["GET","POST", "DELETE"])
def journalQuotes(): 
    conn = None
    cursor = None
    quote_fail = {
        "message" : "failed to post"
    }
    content_error = {
            "message" : "Length of quote error"
        }
    if request.method == "POST":
        data = request.json
        token = data.get("editorToken")
        quote = data.get("content")
    try:
        if (len(token) == 32):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT editor_id from editor_session WHERE editor_token=?",[token,])
            editor_id = cursor.fetchone()
        #checking if editor is logged in. if so, allow them to create a quote
            if (len(quote) <= 200 and len(quote) > 0):
                cursor.execute("INSERT INTO quote(content) VALUES (?)",[quote,])
                conn.commit()
                cursor.execute("SELECT * FROM quote WHERE content=?",[quote,])
                a_quote = cursor.fetchone()
                resp = {
                    "quoteId": a_quote[0],
                    "content" : a_quote[1]
                }
                return Response(json.dumps(resp, default=str),
                            mimetype='application/json',
                            status=201)
            else:
                    return Response(json.dumps(content_error,default=str),
                                mimetype='application/json',
                                status=400)
        else:
            return Response(json.dumps(quote_fail,default=str),
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
        id = params.get("quoteId")
    try:
        if(len(params) == 1):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quote WHERE id=?",[id,])
            select_quote = cursor.fetchone()
            the_quote = {
                "quoteId" : select_quote[0],
                "content" : select_quote[1]
            }
            return Response(json.dumps(the_quote, default=str),
                            mimetype='application/json',
                            status=200)
        else:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quote")
            the_quotes = cursor.fetchall()
            all_quotes = []
            for quote in the_quotes:
                coll = {
                    "quoteId" : quote[0],
                    "content" : quote[1]
                }
                all_quotes.append(coll)
            return Response(json.dumps(all_quotes, default=str),
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

    if request.method == "DELETE":
        data = request.json
        Etoken = data.get("editorToken")
        quoteID = data.get("quoteId")
        delete_fail = {
            "message" : "something went wrong with deleting quote"
        }
        confirm = {
            "message" : "quote deleted"
        }
        data_error = {
            "message" : "something wrong with passed data"
        }
        if (len(Etoken) == 32 and isinstance(quoteID, int) == True):
            try:
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT editor_id FROM editor_session WHERE editor_token=?",[Etoken,])
                session_editorID = cursor.fetchone()
                if(len(session_editorID)==1):
                    cursor.execute("DELETE from quote WHERE id=?",[quoteID])
                    conn.commit()
                    return Response(json.dumps(confirm, default=str),
                                        mimetype="application/json",
                                        status=200)
                else:
                    return Response(json.dumps(delete_fail, default=str),
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
        else:
            return Response(json.dumps(data_error, default=str),
                                mimetype='application/json',
                                status=401)