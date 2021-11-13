from journal import app
from flask import Flask, request, Response
import mariadb
import dbcreds
import json

@app.route("/api/books", methods=["GET","POST", "DELETE"])
def journalBooks(): 
    conn = None
    cursor = None
    book_fail = {
        "message" : "failed to post"
    }
    content_error = {
            "message" : "Length of url error"
        }
    if request.method == "POST":
        data = request.json
        token = data.get("editorToken")
        imgLink = data.get("imageURL")
        shopLink = data.get("shopURL")
        title = data.get("title")
        author = data.get("author")
        if_empty = {
            "message" : "Enter in required data"
        }
        #before connecting the db check the passed data. checks image link length below in if statement
        if (title == ''):
            return Response(json.dumps(if_empty, default=str),
                                mimetype='application/json',
                                status=400)
        if (author == ''):
            return Response(json.dumps(if_empty, default=str),
                                mimetype='application/json',
                                status=400)
        if (shopLink == ''):
                return Response(json.dumps(if_empty, default=str),
                                mimetype='application/json',
                                status=400)

    try:
        if (len(token) == 32):
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT editor_id from editor_session WHERE editor_token=?",[token,])
            editor_id = cursor.fetchone()
        #checking if editor is logged in. if so, allow them to create a book
            if (len(imgLink) <= 300 and len(imgLink) > 0):
                cursor.execute("INSERT INTO book(title, author ,image_URL, shop_URL) VALUES (?,?,?,?)",[title, author, imgLink, shopLink])
                conn.commit()
                cursor.execute("SELECT * FROM book WHERE image_URL=?",[imgLink,])
                a_book = cursor.fetchone()
                resp = {
                    "bookId": a_book[0],
                    "title" : a_book[1],
                    "author" : a_book[2],
                    "imageURL" : a_book[3],
                    "shopURL" : a_book[4]
                }
                return Response(json.dumps(resp, default=str),
                            mimetype='application/json',
                            status=201)
            else:
                return Response(json.dumps(content_error,default=str),
                                mimetype='application/json',
                                status=400)
        else:
            return Response(json.dumps(book_fail,default=str),
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
        try:
            conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM book")
            the_books = cursor.fetchall()
            all_books = []
            for book in the_books:
                coll = {
                    "bookId" : book[0],
                    "title" : book[1],
                    "author" : book[2],
                    "imageURL" : book[3],
                    "shopURL" : book[4]
                }
                all_books.append(coll)
            return Response(json.dumps(all_books, default=str),
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
        Etoken = data.get("editorToken")
        bookID = data.get("bookId")
        delete_fail = {
            "message" : "something went wrong with deleting the book"
        }
        confirm = {
            "message" : "book deleted"
        }
        data_error = {
            "message" : "something wrong with passed data"
        }
        if (len(Etoken) == 32 and isinstance(bookID, int) == True):
            try:
                conn = mariadb.connect(user=dbcreds.user,password=dbcreds.password,host=dbcreds.host,port=dbcreds.port,database=dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT editor_id FROM editor_session WHERE editor_token=?",[Etoken,])
                session_editorID = cursor.fetchone()
                if(len(session_editorID)==1):
                    cursor.execute("DELETE from book WHERE id=?",[bookID])
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