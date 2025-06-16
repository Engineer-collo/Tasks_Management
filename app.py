from flask import Flask, request, make_response, jsonify
from models import db, Todo, User, Profile
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import cloudinary, cloudinary.uploader
from datetime import timedelta

app = Flask(__name__)

app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config ['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
     #Set secret key
app.config['JWT_SECRET_KEY'] = 'shHjkNYYjYOdZAP-7uQPy4Me85N3x6MTNDw_dM4q9SkW0IXEGXz7VclYgUuX41uI'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

    #cloudinary configuration
cloudinary.config(
 cloud_name='dmdlko3to',
 api_key='534181142471392',
  api_secret='WeVNP9uhF7sua9eyahjWhhT2tN0',
 secure=True
)

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)
jwt = JWTManager(app)

@app.route('/')
def index():
    return 'Hello from my Flask app!'

# C - create -mthod == "POST"
# R - read - read_all, read_specific_id -method == "GET"
# U - update -method == "PUT,PATCH"
# D - delete -method == "DELETE"

#====================================CRUD FOR TODOs============================

#-------------------create task------------------
@app.route('/todo', methods=['POST'])
@jwt_required()
def create_task():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('content'):
        return make_response(jsonify({'error': 'Content is required!'}), 400)

    new_task = Todo(content=data['content'], user_id=current_user_id)

    db.session.add(new_task)
    db.session.commit()

    return jsonify(new_task.to_dict()), 201
 
#-------------------get all tasks----------------
@app.route('/todo', methods=["GET"])
@jwt_required()
def get_all_tasks():
    current_user_id = get_jwt_identity()

    # Only fetch tasks created by the logged-in user
    tasks = Todo.query.filter_by(user_id=current_user_id).all()
    response = [task.to_dict() for task in tasks]
    
    return make_response(jsonify(response), 200)

#-------------------get task by id ---------------
@app.route('/todo/<int:id>', methods=["GET"])
@jwt_required()
def get_task_by_id(id):
    current_user_id = get_jwt_identity()
    task = Todo.query.get_or_404(id)

    if task.user_id != current_user_id:
        return make_response(jsonify({"error": "Unauthorized access"}), 403)

    return make_response(jsonify(task.to_dict()), 200)

#-------------------update task-------------------
@app.route('/todo/<int:id>', methods=["PUT", "PATCH"])
@jwt_required()
def update_task(id):
    current_user_id = get_jwt_identity()

    # get task to update
    task = Todo.query.get_or_404(id)

    # Check if the task belongs to the current user
    if task.user_id != current_user_id:
        return make_response(jsonify({"error": "Unauthorized"}), 403)

    updated_data = request.get_json()
    if not updated_data or not updated_data.get("content"):
        return make_response(jsonify({"error": "Content required"}), 400)

    # update the content
    task.content = updated_data["content"]
    db.session.commit()

    return make_response(jsonify(task.to_dict()), 200)

#--------------------delete task-------------------
@app.route('/todo/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_task(id):
    current_user_id = get_jwt_identity()

    # Fetch the task by its ID
    task = Todo.query.get_or_404(id)

    #Optional: Prevent users from deleting tasks they don't own
    if task.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized access'}), 403

    db.session.delete(task)
    db.session.commit()

    return make_response(jsonify(task.to_dict()), 200)

#====================================CRUD FOR USER============================

#---------------------create user-----------------
@app.route('/register', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return make_response(jsonify({'error': 'Email and password are required.'}), 400)

    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return make_response(jsonify({'error': 'User already exists.'}), 409)

    # Create and save user
    new_user = User(email=data['email'])
    new_user.set_password(data['password'])  # Hash the plain-text password
    db.session.add(new_user)
    db.session.commit()

    return make_response(jsonify({
        'message': 'User created successfully.',
        'user': new_user.to_dict()
    }), 201)

#---------------------get user---------------------
@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    if not users:
        return make_response(jsonify({'error' : 'No users found'}), 400)
    response = [user.to_dict() for user in users]
    return make_response(jsonify(response), 200)
    
#---------------------login user--------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and Password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))  # 👈 FIXED HERE
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200

    return jsonify({"error": "Invalid credentials"}), 401


#======================================CRUD FOR PROFILE===========================

#-----------------------------upload profile to cloudinary------------------------
@app.route('/upload_profile_pic', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=user_id).first()

    if 'image' not in request.files:
        return jsonify({"error": "Image file required"}), 400

    image = request.files['image']
    upload_result = cloudinary.uploader.upload(image)
    image_url = upload_result.get('secure_url')

    profile.profile_picture_url = image_url
    db.session.commit()

    return jsonify({
        "message": "Profile picture updated",
        "image_url": image_url
    }), 200


#--------------------------------- get profile------------------------------------
@app.route('/profile/', methods=['GET'])
@jwt_required() 
def get_profile():
    current_user_id = get_jwt_identity() 

    profile = Profile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return make_response(jsonify({'error' : 'Profile not found.'}), 400)
    return make_response(jsonify(profile.to_dict()), 200)

#----------------------------------post profile-----------------------------------
@app.route('/profile', methods=['POST'])
@jwt_required()
def create_profile():
    user_id = get_jwt_identity()

    data = request.get_json()
    if not data:
        return make_response(jsonify({'error': 'Missing profile data'}), 400)

    username = data.get('username', '').strip()
    bio = data.get('bio', '').strip()
    profile_picture_url = data.get('profile_picture_url', '').strip()

    if not username or not bio or not profile_picture_url:
        return make_response(jsonify({'error': 'All fields are required'}), 400)

    if Profile.query.filter_by(user_id=user_id).first():
        return make_response(jsonify({'error': 'Profile already exists'}), 400)

    new_profile = Profile(
        username=username,
        bio=bio,
        profile_picture_url=profile_picture_url,
        user_id=user_id
    )

    db.session.add(new_profile)
    db.session.commit()

    return make_response(jsonify({'message': 'Profile created successfully', 'profile': new_profile.to_dict()}), 201)

#----------------------------------put profile------------------------------------
@app.route('/profile', methods=['PUT', 'PATCH'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()

    data = request.get_json()

    username = data.get('username')
    bio = data.get('bio')
    profile_picture_url = data.get('profile_picture_url')

    if not username or not bio or not profile_picture_url:
        return make_response(jsonify({'error': 'All fields are required'}), 400)

    profile = Profile.query.filter_by(user_id=current_user_id).first()

    if not profile:
        return make_response(jsonify({'error': 'Profile not found. Please create one first.'}), 404)

    # Update fields
    profile.username = username
    profile.bio = bio
    profile.profile_picture_url = profile_picture_url

    db.session.commit()

    return make_response(jsonify({'message': 'Profile updated successfully', 'profile': profile.to_dict()}), 200)

#----------------------------------delete profile---------------------------------
@app.route('/profile', methods=['DELETE'])
@jwt_required()
def delete_profile():
    current_user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=current_user_id).first()

    if not profile:
        return make_response(jsonify({'error': 'Profile not found'}), 404)

    db.session.delete(profile)
    db.session.commit()

    return make_response(jsonify({'message': 'Profile deleted successfully'}), 200)

if __name__ == "__main__":
    app.run(debug=True)




