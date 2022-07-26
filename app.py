from heresourplan import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True) #running the app


#in terminal -> from app import db
#imports db variable 
#db.create_all() -> create all the tables in the app file into db file



#mysql database.db -> in terminal -> checking whether changes are applied
#.tables -> checking each table
#.exit -> exit








# @app.get("/useractivity")
# def joining_activity():
#     activity = Activity.query.all()
#     joining = Activity.query.join(
#         Activity, 
#         Activity.id==UserActivity.activity
#     ).add_columns(
#         Activity.id, 
#         Activity.img, 
#         Activity.mimetype, 
#         Activity.imgfilename, 
#         UserActivity.username, 
#         UserActivity.rank
#     ).all()
#     print(joining)
#     db.session.commit()

#     return "Activity Table Joined!"





# def act_decode_img(img):
#     return base64.b64encode.decode('utf-8')






# def joining_tables_profile():
#     user = User.query.all()
#     User.query.join(User, user.id==UserActivity.username).add_columns(User.id, User.img, User.mimetype, User.imgfilename, UserActivity.activity_id, UserActivity.rank)

#     db.session.commit()

#     return "user table joined!"



# def profile_convert_to_base_to_img():
#     user_img = request.form["img"]
#     with open(user_img, "rb") as img_file:
#         encoded_string = base64.b64encode(img_file.read())
    
    # return encoded_string.decode('utf-8')


