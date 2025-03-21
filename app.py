

# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# from pymongo import MongoClient
# import base64
# import uuid
# import os
# import io  # ✅ Add this line at the top
# from PIL import Image
# from deepface import DeepFace
# import numpy as np
# from bson.objectid import ObjectId
# from werkzeug.security import generate_password_hash, check_password_hash
# import uuid

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# # ✅ Ensure OPTIONS requests are handled correctly
# @app.before_request
# def handle_options_request():
#     if request.method == "OPTIONS":
#         return jsonify({"message": "CORS Preflight OK"}), 200
# # MongoDB Setup
# client = MongoClient("mongodb://localhost:27017")
# db = client["photo_gallery"]
# albums_collection = db["albums"]
# db = client["dist_and_depart"]
# districts_collection = db["districts"]
# departments_collection = db["departments"]
# auth_db = client["auth_db"]
# users_collection = auth_db["users"]




# MODEL_PATH = os.path.join(os.path.dirname(__file__), "facenet_keras.h5")

# # Helper function: Compress Image

# def compress_image(image_base64, quality=50):
#     """
#     Decodes a base64 image, compresses it, and returns the compressed image as base64.
#     Converts RGBA to RpythonGB if necessary (JPEG does not support transparency).
#     """
#     try:
#         # ✅ Decode base64 image into bytes
#         image_bytes = base64.b64decode(image_base64)
#         image = Image.open(io.BytesIO(image_bytes))  # ✅ Convert bytes to PIL Image

#         # ✅ Fix: Convert RGBA to RGB before saving as JPEG
#         if image.mode == "RGBA":
#             image = image.convert("RGB")

#         # ✅ Compress the image
#         output_io = io.BytesIO()
#         image.save(output_io, format="JPEG", quality=quality)
#         output_io.seek(0)

#         # ✅ Encode the compressed image back to base64
#         compressed_base64 = base64.b64encode(output_io.getvalue()).decode("utf-8")
#         return compressed_base64

#     except Exception as e:
#         print("Error compressing image:", str(e))
#         return None

# # Helper function: Extract Face Embeddings
# def extract_faces(image_data):
#     image_path = f"temp_{uuid.uuid4().hex}.jpg"
#     with open(image_path, "wb") as f:
#         f.write(base64.b64decode(image_data))

#     try:
#         print(f"✅ Using local model at {MODEL_PATH}")
        
#         # ✅ Explicitly pass the model path to DeepFace
#         faces = DeepFace.represent(image_path, model_name="Facenet", model_path=MODEL_PATH)

#         os.remove(image_path)
#         return [{"face_id": str(uuid.uuid4()), "embedding": np.array(face["embedding"]).tolist()} for face in faces]

#     except Exception as e:
#         print(f"❌ Error in face extraction: {e}")
#         os.remove(image_path)
#         return []

# @app.route("/")
# def home():
#     return jsonify({"message": "Backend is running successfully!"}), 200
# # API: Create Album
# @app.route("/create-album", methods=["POST"])
# def create_album():
#     data = request.json
#     album = {
#         "_id": str(uuid.uuid4()),
#         "name": data["name"],
#         "date": data["date"],
#         "cover": data["cover"],
#         "department": data.get("department", ""),  # ✅ Store department
#         "districts": data.get("districts", []),
#         "photos": []
#     }
#     albums_collection.insert_one(album)
#     return jsonify({"message": "Album created successfully"}), 201

# # API: Upload Photos to Album
# @app.route("/upload-gallery/<album_id>", methods=["POST"])
# def upload_gallery(album_id):
#     data = request.json
#     album = albums_collection.find_one({"_id": album_id})
#     if not album:
#         return jsonify({"error": "Album not found"}), 404

#     new_photos = []
#     for image in data.get("images", []):  # ✅ Use `.get()` to avoid KeyErrors
#         if not image or not isinstance(image, str):
#             print("❌ Invalid image received:", image)  # Debugging log
#             continue  # Skip invalid images

#         compressed_image = compress_image(image)
#         if not compressed_image:
#             return jsonify({"error": "Image compression failed"}), 500

#         new_photos.append({
#             "photo_id": str(uuid.uuid4()),
#             "image": compressed_image,
#             "face_embeddings": extract_faces(image)
#         })

#     if new_photos:
#         albums_collection.update_one({"_id": album_id}, {"$push": {"photos": {"$each": new_photos}}})
#         return jsonify({"message": "Photos uploaded successfully"}), 200
#     else:
#         return jsonify({"error": "No valid images uploaded"}), 400

# # API: Get Albums
# @app.route("/albums", methods=["GET"])
# def get_albums():
#     albums = list(albums_collection.find({}, {"_id": 1, "name": 1, "date": 1, "cover": 1}))
#     return jsonify(albums)

# # API: Get Photos from Album
# @app.route('/photos/<album_id>', methods=['GET'])
# def get_album_photos(album_id):
#     album = albums_collection.find_one({"_id": album_id})  # ✅ Corrected reference
#     if not album:
#         return jsonify({"error": "Album not found"}), 404

#     photos = album.get("photos", [])
    
#     photos_base64 = []
#     for photo in photos:
#         image_data = photo.get("image")
#         if not image_data:
#             print(f"Skipping invalid photo: {photo}")
#             continue

#         if not image_data.startswith("data:image/"):
#             image_data = f"data:image/jpeg;base64,{image_data}"
        
#         photos_base64.append({
#             "photo_id": photo.get("photo_id"),
#             "image": image_data
#         })

#     return jsonify(photos_base64)



# # API: Delete Album
# @app.route("/album/<album_id>", methods=["DELETE"])
# def delete_album(album_id):
#     result = albums_collection.delete_one({"_id": album_id})
#     if result.deleted_count == 0:
#         return jsonify({"error": "Album not found"}), 404
#     return jsonify({"message": "Album deleted successfully"}), 200

# # API: Delete Photo from Album
# @app.route("/photo/<album_id>/<photo_id>", methods=["DELETE"])
# def delete_photo(album_id, photo_id):
#     print(f"🔍 Deleting photo {photo_id} from album {album_id}")
    
#     album = albums_collection.find_one({"_id": album_id}, {"photos": 1})
#     if not album:
#         return jsonify({"error": "Album not found"}), 404

#     print(f"✅ Found album: {album}")

#     result = albums_collection.update_one(
#     {"_id": album_id},
#     {"$pull": {"photos": {"photo_id": str(photo_id)}}}  # ✅ Convert `photo_id` to string
# )


#     print(f"🛠️ MongoDB update result: {result.raw_result}")

#     if result.modified_count == 0:
#         return jsonify({"error": "Photo not found"}), 404

#     return jsonify({"message": "Photo deleted successfully"}), 200



# from bson.objectid import ObjectId  # ✅ Add this import

# @app.route("/delete-albums", methods=["DELETE"])
# def delete_multiple_albums():
#     data = request.json
#     album_ids = data.get("albumIds", [])

#     if not album_ids:
#         return jsonify({"error": "No album IDs provided"}), 400

#     result = albums_collection.delete_many({"_id": {"$in": album_ids}})  # Keep IDs as strings

#     return jsonify({"message": f"Deleted {result.deleted_count} albums successfully"}), 200



# # API: Get all districts
# @app.route("/districts", methods=["GET"])
# def get_districts():
#     districts = list(districts_collection.find({}, {"_id": 0}))
#     return jsonify(districts)

# # API: Add a new district
# @app.route("/districts", methods=["POST"])
# def add_district():
#     data = request.json
#     if "name" not in data:
#         return jsonify({"error": "District name is required"}), 400
#     districts_collection.insert_one({"name": data["name"]})
#     return jsonify({"message": "District added successfully"}), 201

# # API: Edit a district
# @app.route("/districts/<string:old_name>", methods=["PUT"])
# def edit_district(old_name):
#     data = request.json
#     if "name" not in data:
#         return jsonify({"error": "New district name is required"}), 400
#     districts_collection.update_one({"name": old_name}, {"$set": {"name": data["name"]}})
#     return jsonify({"message": "District updated successfully"}), 200

# # API: Delete a district
# @app.route("/districts/<string:name>", methods=["DELETE"])
# def delete_district(name):
#     districts_collection.delete_one({"name": name})
#     return jsonify({"message": "District deleted successfully"}), 200

# # API: Get all departments
# @app.route("/departments", methods=["GET"])
# def get_departments():
#     departments = list(departments_collection.find({}, {"_id": 0}))
#     return jsonify(departments)

# # API: Add a new department
# @app.route("/departments", methods=["POST"])
# def add_department():
#     data = request.json
#     if "name" not in data:
#         return jsonify({"error": "Department name is required"}), 400
#     departments_collection.insert_one({"name": data["name"]})
#     return jsonify({"message": "Department added successfully"}), 201

# # API: Edit a department
# @app.route("/departments/<string:old_name>", methods=["PUT"])
# def edit_department(old_name):
#     data = request.json
#     if "name" not in data:
#         return jsonify({"error": "New department name is required"}), 400
#     departments_collection.update_one({"name": old_name}, {"$set": {"name": data["name"]}})
#     return jsonify({"message": "Department updated successfully"}), 200

# # API: Delete a department
# @app.route("/departments/<string:name>", methods=["DELETE"])
# def delete_department(name):
#     departments_collection.delete_one({"name": name})
#     return jsonify({"message": "Department deleted successfully"}), 200



# # API: Add New Staff Member
# @app.route("/add-staff", methods=["POST"])
# def add_staff():
#     data = request.json

#     # Validate required fields
#     required_fields = ["name", "email", "mobile", "password", "district"]
#     if not all(field in data for field in required_fields):
#         return jsonify({"error": "Missing required fields"}), 400

#     # Hash the password
#     hashed_password = generate_password_hash(data["password"])

#     # Create user document
#     new_user = {
#         "_id": str(uuid.uuid4()),
#         "name": data["name"],
#         "email": data["email"],
#         "mobile": data["mobile"],
#         "district": data["district"],
#         "role": "Admin",  # Default role
#         "password": hashed_password,  # Store only the hashed password
#         "status": True  # Default status
#     }

#     # Insert into database
#     users_collection.insert_one(new_user)

#     return jsonify({"message": "Staff added successfully"}), 201


# # ✅ API to Update User Data
# @app.route("/update-user/<string:user_id>", methods=["PUT"])
# def update_user(user_id):
#     data = request.json
#     update_fields = {}

#     # Allow status updates along with other fields
#     for field in ["name", "email", "mobile", "district", "status"]:
#         if field in data:
#             update_fields[field] = data[field]

#     if not update_fields:
#         return jsonify({"error": "No fields to update"}), 400

#     result = users_collection.update_one({"_id": user_id}, {"$set": update_fields})

#     if result.modified_count == 0:
#         return jsonify({"error": "User not found or no changes made"}), 404

#     return jsonify({"message": "User updated successfully"}), 200
# # API: Get All Users
# @app.route("/users", methods=["GET"])
# def get_users():
#     users = list(users_collection.find({}, {"password": 0})) 
#     for user in users:
#         user["_id"] = str(user["_id"])  # Convert ObjectId to string
#         user.setdefault("photo", "/default-profile.png") # Exclude password
#     return jsonify(users)






# @app.route("/upload-photo", methods=["POST"])
# def upload_photo():
#     user_id = request.form.get("userId")
#     photo = request.files.get("photo")

#     if not user_id or not photo:
#         return jsonify({"error": "Missing user ID or photo"}), 400

#     # Convert photo to base64
#     photo_base64 = base64.b64encode(photo.read()).decode('utf-8')

#     # Update the user's profile with base64 photo
#     users_collection.update_one({"_id": user_id}, {"$set": {"photo": photo_base64}})

#     return jsonify({"message": "Photo uploaded successfully!", "photo": photo_base64}), 200


# @app.route("/uploads/<filename>")
# def serve_photo(filename):
#     return send_file(f"uploads/{filename}", mimetype="image/jpeg")


# @app.route("/login", methods=["POST"])
# def login():
#     data = request.json
#     identifier = data.get("identifier")  # Can be username or mobile
#     password = data.get("password")

#     user = users_collection.find_one({"$or": [{"name": identifier}, {"mobile": identifier}]})
    
#     if not user or not check_password_hash(user["password"], password):
#         return jsonify({"error": "Invalid credentials"}), 401

#     return jsonify({
#         "message": "Login successful",
#         "userId": str(user["_id"]),
#         "name": user["name"],
#         "mobile": user["mobile"],
#         "district": user["district"]
#     }), 200




# @app.route("/get-events", methods=["GET"])
# def get_events():
#     events = albums_collection.find({}, {"name": 1, "_id": 0})  # Use the correct collection & field name
#     event_names = [event["name"] for event in events]  # Extract event names
#     return jsonify(event_names)

# @app.route("/fetch-album-photos", methods=["POST", "OPTIONS"])  # ✅ Added OPTIONS method
# def fetch_album_photos():
#     if request.method == "OPTIONS":  
#         return jsonify({"message": "CORS Preflight OK"}), 200  # ✅ Handle preflight request

#     data = request.json
#     event_name = data.get("eventName")

#     if not event_name:
#         return jsonify({"error": "Event name is required"}), 400

#     album = albums_collection.find_one({"name": event_name})

#     if not album:
#         return jsonify({"error": "No album found with this name"}), 404

#     photos = album.get("photos", [])

#     return jsonify({
#         "photos": [{"photo_id": photo["photo_id"], "image": photo["image"]} for photo in photos]
#     })



# @app.route("/fetch-photos-by-date", methods=["POST", "OPTIONS"])  # ✅ Handle CORS preflight
# def fetch_photos_by_date():
#     if request.method == "OPTIONS":  
#         return jsonify({"message": "CORS Preflight OK"}), 200  # ✅ CORS preflight response

#     data = request.json
#     selected_date = data.get("date")

#     # Validate input
#     if not selected_date:
#         return jsonify({"error": "Date is required in YYYY-MM-DD format"}), 400

#     # Query all documents where "date" matches the selected_date
#     albums = albums_collection.find({"date": selected_date})

#     all_photos = []
    
#     # Iterate through matching albums and collect all photos
#     for album in albums:
#         all_photos.extend([
#             {"photo_id": photo["photo_id"], "image": photo["image"]}
#             for photo in album.get("photos", [])
#         ])

#     if not all_photos:
#         return jsonify({"error": "No photos found for this date"}), 404

#     return jsonify({"photos": all_photos})  # ✅ Return all found photos


# if __name__ == "__main__":
#     port = int(os.getenv("PORT", 5000))  # Get PORT from Render, default to 5000
#     app.run(host="0.0.0.0", port=port, debug=False)






from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
import base64
import uuid
import os
import io  # ✅ Add this line at the top
from PIL import Image
from deepface import DeepFace
import numpy as np
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import zipfile


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://167.86.74.16:3000"]}}, supports_credentials=True)

# ✅ Ensure OPTIONS requests are handled correctly
@app.before_request
def handle_options_request():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS Preflight OK"}), 200
# MongoDB Setup
client = MongoClient("mongodb+srv://Aayush:Aayush%402003@photo-gallery.pvd7i.mongodb.net/?retryWrites=true&w=majority&appName=photo-gallery")
db = client["photo_gallery"]
albums_collection = db["albums"]
db = client["dist_and_depart"]
districts_collection = db["districts"]
departments_collection = db["departments"]
auth_db = client["auth_db"]
users_collection = auth_db["users"]




MODEL_PATH = os.path.join(os.path.dirname(__file__), "facenet_keras.h5")

# Helper function: Compress Image

def compress_image(image_base64, quality=50):
    """
    Decodes a base64 image, compresses it, and returns the compressed image as base64.
    Converts RGBA to RpythonGB if necessary (JPEG does not support transparency).
    """
    try:
        # ✅ Decode base64 image into bytes
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))  # ✅ Convert bytes to PIL Image

        # ✅ Fix: Convert RGBA to RGB before saving as JPEG
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # ✅ Compress the image
        output_io = io.BytesIO()
        image.save(output_io, format="JPEG", quality=quality)
        output_io.seek(0)

        # ✅ Encode the compressed image back to base64
        compressed_base64 = base64.b64encode(output_io.getvalue()).decode("utf-8")
        return compressed_base64

    except Exception as e:
        print("Error compressing image:", str(e))
        return None

# Helper function: Extract Face Embeddings
def extract_faces(image_data):
    image_path = f"temp_{uuid.uuid4().hex}.jpg"
    with open(image_path, "wb") as f:
        f.write(base64.b64decode(image_data))

    try:
        print(f"✅ Using local model at {MODEL_PATH}")
        
        # ✅ Explicitly pass the model path to DeepFace
        faces = DeepFace.represent(image_path, model_name="Facenet", model_path=MODEL_PATH)

        os.remove(image_path)
        return [{"face_id": str(uuid.uuid4()), "embedding": np.array(face["embedding"]).tolist()} for face in faces]

    except Exception as e:
        print(f"❌ Error in face extraction: {e}")
        os.remove(image_path)
        return []

@app.route("/")
def home():
    return jsonify({"message": "Backend is running successfully!"}), 200
# API: Create Album
@app.route("/create-album", methods=["POST"])
def create_album():
    data = request.json
    album = {
        "_id": str(uuid.uuid4()),
        "name": data["name"],
        "date": data["date"],
        "cover": data["cover"],
        "department": data.get("department", ""),  # ✅ Store department
        "districts": data.get("districts", []),
        "photos": []
    }
    albums_collection.insert_one(album)
    return jsonify({"message": "Album created successfully"}), 201

# API: Upload Photos to Album
@app.route("/upload-gallery/<album_id>", methods=["POST"])
def upload_gallery(album_id):
    data = request.json
    album = albums_collection.find_one({"_id": album_id})
    if not album:
        return jsonify({"error": "Album not found"}), 404

    new_photos = []
    for image in data.get("images", []):  # ✅ Use `.get()` to avoid KeyErrors
        if not image or not isinstance(image, str):
            print("❌ Invalid image received:", image)  # Debugging log
            continue  # Skip invalid images

        compressed_image = compress_image(image)
        if not compressed_image:
            return jsonify({"error": "Image compression failed"}), 500

        new_photos.append({
            "photo_id": str(uuid.uuid4()),
            "image": compressed_image,
            "face_embeddings": extract_faces(image)
        })

    if new_photos:
        albums_collection.update_one({"_id": album_id}, {"$push": {"photos": {"$each": new_photos}}})
        return jsonify({"message": "Photos uploaded successfully"}), 200
    else:
        return jsonify({"error": "No valid images uploaded"}), 400

# API: Get Albums
@app.route("/albums", methods=["GET"])
def get_albums():
    albums = list(albums_collection.find({}, {"_id": 1, "name": 1, "date": 1, "cover": 1}))
    return jsonify(albums)

# API: Get Photos from Album
@app.route('/photos/<album_id>', methods=['GET'])
def get_album_photos(album_id):
    album = albums_collection.find_one({"_id": album_id})  # ✅ Corrected reference
    if not album:
        return jsonify({"error": "Album not found"}), 404

    photos = album.get("photos", [])
    
    photos_base64 = []
    for photo in photos:
        image_data = photo.get("image")
        if not image_data:
            print(f"Skipping invalid photo: {photo}")
            continue

        if not image_data.startswith("data:image/"):
            image_data = f"data:image/jpeg;base64,{image_data}"
        
        photos_base64.append({
            "photo_id": photo.get("photo_id"),
            "image": image_data
        })

    return jsonify(photos_base64)



# API: Delete Album
@app.route("/album/<album_id>", methods=["DELETE"])
def delete_album(album_id):
    result = albums_collection.delete_one({"_id": album_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Album not found"}), 404
    return jsonify({"message": "Album deleted successfully"}), 200

# API: Delete Photo from Album
@app.route("/photo/<album_id>/<photo_id>", methods=["DELETE"])
def delete_photo(album_id, photo_id):
    print(f"🔍 Deleting photo {photo_id} from album {album_id}")
    
    album = albums_collection.find_one({"_id": album_id}, {"photos": 1})
    if not album:
        return jsonify({"error": "Album not found"}), 404

    print(f"✅ Found album: {album}")

    result = albums_collection.update_one(
    {"_id": album_id},
    {"$pull": {"photos": {"photo_id": str(photo_id)}}}  # ✅ Convert `photo_id` to string
)


    print(f"🛠️ MongoDB update result: {result.raw_result}")

    if result.modified_count == 0:
        return jsonify({"error": "Photo not found"}), 404

    return jsonify({"message": "Photo deleted successfully"}), 200



from bson.objectid import ObjectId  # ✅ Add this import

@app.route("/delete-albums", methods=["DELETE"])
def delete_multiple_albums():
    data = request.json
    album_ids = data.get("albumIds", [])

    if not album_ids:
        return jsonify({"error": "No album IDs provided"}), 400

    result = albums_collection.delete_many({"_id": {"$in": album_ids}})  # Keep IDs as strings

    return jsonify({"message": f"Deleted {result.deleted_count} albums successfully"}), 200



# API: Get all districts
@app.route("/districts", methods=["GET"])
def get_districts():
    districts = list(districts_collection.find({}, {"_id": 0}))
    return jsonify(districts)

# API: Add a new district
@app.route("/districts", methods=["POST"])
def add_district():
    data = request.json
    if "name" not in data:
        return jsonify({"error": "District name is required"}), 400
    districts_collection.insert_one({"name": data["name"]})
    return jsonify({"message": "District added successfully"}), 201

# API: Edit a district
@app.route("/districts/<string:old_name>", methods=["PUT"])
def edit_district(old_name):
    data = request.json
    if "name" not in data:
        return jsonify({"error": "New district name is required"}), 400
    districts_collection.update_one({"name": old_name}, {"$set": {"name": data["name"]}})
    return jsonify({"message": "District updated successfully"}), 200

# API: Delete a district
@app.route("/districts/<string:name>", methods=["DELETE"])
def delete_district(name):
    districts_collection.delete_one({"name": name})
    return jsonify({"message": "District deleted successfully"}), 200

# API: Get all departments
@app.route("/departments", methods=["GET"])
def get_departments():
    departments = list(departments_collection.find({}, {"_id": 0}))
    return jsonify(departments)

# API: Add a new department
@app.route("/departments", methods=["POST"])
def add_department():
    data = request.json
    if "name" not in data:
        return jsonify({"error": "Department name is required"}), 400
    departments_collection.insert_one({"name": data["name"]})
    return jsonify({"message": "Department added successfully"}), 201

# API: Edit a department
@app.route("/departments/<string:old_name>", methods=["PUT"])
def edit_department(old_name):
    data = request.json
    if "name" not in data:
        return jsonify({"error": "New department name is required"}), 400
    departments_collection.update_one({"name": old_name}, {"$set": {"name": data["name"]}})
    return jsonify({"message": "Department updated successfully"}), 200

# API: Delete a department
@app.route("/departments/<string:name>", methods=["DELETE"])
def delete_department(name):
    departments_collection.delete_one({"name": name})
    return jsonify({"message": "Department deleted successfully"}), 200



# API: Add New Staff Member
@app.route("/add-staff", methods=["POST"])
def add_staff():
    data = request.json

    # Validate required fields
    required_fields = ["name", "email", "mobile", "password", "district"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Hash the password
    hashed_password = generate_password_hash(data["password"])

    # Create user document
    new_user = {
        "_id": str(uuid.uuid4()),
        "name": data["name"],
        "email": data["email"],
        "mobile": data["mobile"],
        "district": data["district"],
        "role": "Admin",  # Default role
        "password": hashed_password,  # Store only the hashed password
        "status": True  # Default status
    }

    # Insert into database
    users_collection.insert_one(new_user)

    return jsonify({"message": "Staff added successfully"}), 201


# ✅ API to Update User Data
@app.route("/update-user/<string:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    update_fields = {}

    # Allow status updates along with other fields
    for field in ["name", "email", "mobile", "district", "status"]:
        if field in data:
            update_fields[field] = data[field]

    if not update_fields:
        return jsonify({"error": "No fields to update"}), 400

    result = users_collection.update_one({"_id": user_id}, {"$set": update_fields})

    if result.modified_count == 0:
        return jsonify({"error": "User not found or no changes made"}), 404

    return jsonify({"message": "User updated successfully"}), 200
# API: Get All Users
@app.route("/users", methods=["GET"])
def get_users():
    users = list(users_collection.find({}, {"password": 0})) 
    for user in users:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        user.setdefault("photo", "/default-profile.png") # Exclude password
    return jsonify(users)






@app.route("/upload-photo", methods=["POST"])
def upload_photo():
    user_id = request.form.get("userId")
    photo = request.files.get("photo")

    if not user_id or not photo:
        return jsonify({"error": "Missing user ID or photo"}), 400

    # Convert photo to base64
    photo_base64 = base64.b64encode(photo.read()).decode('utf-8')

    # Update the user's profile with base64 photo
    users_collection.update_one({"_id": user_id}, {"$set": {"photo": photo_base64}})

    return jsonify({"message": "Photo uploaded successfully!", "photo": photo_base64}), 200


@app.route("/uploads/<filename>")
def serve_photo(filename):
    return send_file(f"uploads/{filename}", mimetype="image/jpeg")


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    identifier = data.get("identifier")  # Can be username or mobile
    password = data.get("password")

    user = users_collection.find_one({"$or": [{"name": identifier}, {"mobile": identifier}]})
    
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "message": "Login successful",
        "userId": str(user["_id"]),
        "name": user["name"],
        "mobile": user["mobile"],
        "district": user["district"]
    }), 200




@app.route("/get-events", methods=["GET"])
def get_events():
    events = albums_collection.find({}, {"name": 1, "_id": 0})  # Use the correct collection & field name
    event_names = [event["name"] for event in events]  # Extract event names
    return jsonify(event_names)

@app.route("/fetch-album-photos", methods=["POST", "OPTIONS"])  # ✅ Added OPTIONS method
def fetch_album_photos():
    if request.method == "OPTIONS":  
        return jsonify({"message": "CORS Preflight OK"}), 200  # ✅ Handle preflight request

    data = request.json
    event_name = data.get("eventName")

    if not event_name:
        return jsonify({"error": "Event name is required"}), 400

    album = albums_collection.find_one({"name": event_name})

    if not album:
        return jsonify({"error": "No album found with this name"}), 404

    photos = album.get("photos", [])

    return jsonify({
        "photos": [{"photo_id": photo["photo_id"], "image": photo["image"]} for photo in photos]
    })



@app.route("/fetch-photos-by-date", methods=["POST", "OPTIONS"])  # ✅ Handle CORS preflight
def fetch_photos_by_date():
    if request.method == "OPTIONS":  
        return jsonify({"message": "CORS Preflight OK"}), 200  # ✅ CORS preflight response

    data = request.json
    selected_date = data.get("date")

    # Validate input
    if not selected_date:
        return jsonify({"error": "Date is required in YYYY-MM-DD format"}), 400

    # Query all documents where "date" matches the selected_date
    albums = albums_collection.find({"date": selected_date})

    all_photos = []
    
    # Iterate through matching albums and collect all photos
    for album in albums:
        all_photos.extend([
            {"photo_id": photo["photo_id"], "image": photo["image"]}
            for photo in album.get("photos", [])
        ])

    if not all_photos:
        return jsonify({"error": "No photos found for this date"}), 404

    return jsonify({"photos": all_photos})  # ✅ Return all found photos


@app.route('/photo-base64/<photo_id>', methods=['GET'])
def get_photo_base64(photo_id):
    album = albums_collection.find_one({"photos.photo_id": photo_id}, {"photos.$": 1})
    if not album or "photos" not in album or not album["photos"]:
        return jsonify({"error": "Photo not found"}), 404

    photo = album["photos"][0]
    return jsonify({"photo_id": photo["photo_id"], "image": photo["image"]})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Get PORT from Render, default to 5000
    app.run(host="0.0.0.0", port=port, debug=False)




