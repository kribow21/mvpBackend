from journal import app
import sys

if(len(sys.argv) > 1):
    mode = sys.argv[1]
    if(mode == "production"):
        import bjoern
        host = "0.0.0.0"
        port = 5002
        print("server is running in production code")
        bjoern.run(app,host, port )
    elif(mode == "testing"):
        from flask_cors import CORS
        CORS(app)
        print("server is running in testing mode, switch to production when needed")
        app.run(debug=True)
    else:
        print("invalid mode arguments, exiting")
        exit()
else:
    print("There was no argument provided")
    exit()