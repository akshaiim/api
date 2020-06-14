from flask import Flask, url_for, jsonify, abort, make_response, request
from flask_httpauth import HTTPBasicAuth
import mysql.connector, hashlib

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="password",
  database="users"
)



auth = HTTPBasicAuth()


app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]


    
@app.route('/userpass', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    password=hashlib.md5(password.encode())
    password=password.hexdigest()
    if username is None or password is None:
        abort(400) # missing argument
    c = mydb.cursor()
    sql="Insert into userlogin(Username,Password) values (%s, %s)"
    value=(username,password)
    c.execute(sql,value)
    mydb.commit()
    return jsonify({ 'username':username , "password": password}), 201


@app.route('/usersignin', methods = ['POST'])
def sign_in():
    username = request.json.get('username')
    password = request.json.get('password')
    password=hashlib.md5(password.encode())
    password=password.hexdigest()
    if username is None or password is None:
        abort(400) # missing argument
    c = mydb.cursor()
    sql="select * from userlogin where Username=%s and Password=%s"
    value=(username,password)
    c.execute(sql,value)
    result=c.fetchall()
    for data in result:
        if(len(data) == 0):
            abort(400)
                
        else:
            return jsonify({ 'username':username , "password": password}), 201
            




@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return "not a valid string"

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)



@app.route("/tasks",methods=["GET"])
@auth.login_required
def get_tasks():
    return jsonify({"tasks": [make_public_task(task) for task in tasks]})

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task




@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = [task for task in tasks if task["id"] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({"task": task[0]})





@app.route("/tasks", methods=["POST"])
def create_task():
    if not request.json or not "title" in request.json:
        abort(400)
    task = {
        "id": tasks[-1]["id"] + 1,
        "description" : request.json.get("description", ""),
        "done": False,
        "title": request.json["title"]
        }
    tasks.append(task)
    return jsonify({"task" : task}), 201






@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = [task for task in tasks if task["id"] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    
    return jsonify({"value": True})


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def put_task(task_id):
    task = [task for task in tasks if task["id"] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    task[0]["title"] = request.json.get("title", task[0]["title"])
    task[0]["description"] = request.json.get("description", task[0]["description"])
    task[0]["id"] = request.json.get("id", task[0]["id"])
    task[0]["done"] = request.json.get("done", task[0]["done"])
    return jsonify({"task": task[0]})





@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)







if __name__ == "__main__":
    app.run(debug=True,use_reloader=False)