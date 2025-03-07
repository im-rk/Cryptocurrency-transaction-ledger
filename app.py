from flask import Flask,request,flash,redirect,render_template,url_for
import pymongo
from final import obj,generate_wallet_address,collection,users_collection

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Register"]
user_collection = db["users"] 
app=Flask(__name__)
app.secret_key = "f8d9a6c5e9b2a7d0e3f1c4b8a2d6e9f0"

@app.route('/')
def menu():
    return render_template('menu.html')
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='POST':
        user_name=request.form['username']
        password=request.form['password']

        if user_collection.find_one({'username':user_name}):
            flash('Username already exists. Choose a different one.', 'danger')
        else:
            user_collection.insert_one({"username":user_name, "password":password})
            flash('Registration successful. You can now log in.', 'success')
            generate_wallet_address(user_name)
            return redirect(url_for('menu'))
            
            
    return render_template("register.html")
@app.route('/methods')
def methods():
    return render_template('methods.html')
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        user_name = request.form['username']
        password=request.form['password']
        if user_collection.find_one({"username":user_name,"password":password}):
            flash("succesfully login")
            global add 
            add=users_collection.find_one({"name":user_name},{"_id":0,"wallet_address":1})
            add=add['wallet_address']
            print(add)
            return redirect(url_for('methods'))
        else:
            flash("incorrect username or password. try again.")
    return render_template("login.html")

@app.route('/make_trans',methods=['POST','GET'])
def make_trans():
    if request.method=='POST':
        sender=request.form['sender']
        receiver=request.form['receiver']
        amount=request.form['amount']
        obj.add_transaction(sender,receiver,amount)

    return render_template("make_trans.html")

@app.route('/view_trans',methods=['POST','GET'])
def view_trans():
    my_data=collection.find({"sender_address":add})
    return render_template("view_trans.html",my_data=my_data)


if __name__=="__main__":
    app.run(debug=True)


