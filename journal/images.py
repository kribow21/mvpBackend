from journal import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json

@app.route("/api/images", methods=["GET","POST", "DELETE"])
def journalImages(): 
    conn = None
    cursor = None
    img_fail = {
        "message" : "failed to post"
    }
    content_error = {
            "message" : "Length of url error"
        }
    if request.method == "POST":
        data = request.json
        token = data.get("editorToken")
        imgLink = data.get("imageURL")
    try:
        if (len(token) == 32):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT editor_id from editor_session WHERE editor_token=?",[token,])
            editor_id = cursor.fetchone()
        #checking if editor is logged in. if so, allow them to create a quote
            if (len(imgLink) <= 300 and len(imgLink) > 0):
                cursor.execute("INSERT INTO image(image_URL) VALUES (?)",[imgLink,])
                conn.commit()
                cursor.execute("SELECT * FROM image WHERE image_URL=?",[imgLink,])
                a_img = cursor.fetchone()
                resp = {
                    "imageId": a_img[0],
                    "imageURL" : a_img[1]
                }
                return Response(json.dumps(resp, default=str),
                            mimetype='application/json',
                            status=201)
            else:
                return Response(json.dumps(content_error,default=str),
                                mimetype='application/json',
                                status=400)
        else:
            return Response(json.dumps(img_fail,default=str),
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