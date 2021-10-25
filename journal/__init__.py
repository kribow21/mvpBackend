from flask import Flask, request, Response


app= Flask(__name__)

import journal.users
import journal.editors
import journal.userlogin
import journal.editorlogin