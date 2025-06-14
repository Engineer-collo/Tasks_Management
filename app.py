from flask import Flask, request, make_response, jsonify
from models import db, Todo
from flask_migrate import Migrate
from flask_cors import CORS
app = Flask(__name__)

app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config ['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

@app.route('/')
def index():
    return 'Hello from my Flask app!'

# C - create -mthod == "POST"
# R - read - read_all, read_specific_id -method == "GET"
# U - update -method == "PUT,PATCH"
# D - delete -method == "DELETE"

#-------------------create task------------------
@app.route('/todo', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data:
            return make_response(jsonify({'error' : 'Content is required!'}), 400)
    new_task = Todo(content=data['content'])
    db.session.add(new_task)
    db.session.commit()

    return jsonify(new_task.to_dict()), 201
 
#-------------------get all tasks----------------
@app.route('/todo', methods=["GET"])
def get_all_tasks():
    tasks = Todo.query.all()
    response = [task.to_dict() for task in tasks ]
    return make_response(jsonify(response), 200)

#-------------------get task by id ---------------
@app.route('/todo/<int:id>', methods=["GET"])
def get_task_by_id(id):
    task = Todo.query.get_or_404(id)
    response = jsonify(task.to_dict())
    return make_response(response, 200)

#-------------------update task-------------------
@app.route('/todo/<int:id>', methods=["PUT", "PATCH"])
def update_task(id):
    # get task to update
    task = Todo.query.get_or_404(id)

    updated_data = request.get_json()
    if not updated_data or not updated_data.get("content"):
        return make_response(jsonify({"error": "Content required"}), 400)

    # update the content
    task.content = updated_data["content"]
    db.session.commit()

    return make_response(jsonify(task.to_dict()), 200)

#--------------------delete task-------------------
@app.route('/todo/<int:id>', methods=["DELETE"])
def delete_task(id):
     task = Todo.query.get_or_404(id)
     db.session.delete(task)
     db.session.commit()
     
     return make_response(jsonify(task.to_dict()), 200)
    

    

        


    

    



















if __name__ == "__main__":
    app.run(debug=True)