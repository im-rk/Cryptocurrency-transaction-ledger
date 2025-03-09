from flask import Flask,request,flash,redirect,render_template,url_for,session
import pymongo
from final import obj,generate_wallet_address,collection,users_collection
from datetime import datetime

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
            session['username'] = user_name
            add=users_collection.find_one({"name":user_name},{"_id":0,"wallet_address":1})
            session['wallet_address'] = add['wallet_address']
            print(add)
            return redirect(url_for('methods'))
        else:
            flash("incorrect username or password. try again.")
    return render_template("login.html")

@app.route('/make_trans',methods=['POST','GET'])
def make_trans():
    if 'username' not in session:
        flash('please log in first.',"warning")
        return redirect(url_for("login"))

    sender=session['username']

    if request.method=='POST':
        receiver=request.form['receiver']
        if sender==receiver:
            flash("Payment cannot be done within yourself.")
            return redirect(url_for('make_trans'))
        if not users_collection.find_one({"name": receiver}):  
            flash("Invalid user. Try with the correct name.", "danger")
            return redirect(url_for('make_trans')) 
        amount=request.form['amount']
        try:
            amount = float(amount)
            if amount <= 0:
                flash("Invalid amount. Please enter a positive number.", "danger")
                return redirect(url_for('make_trans'))
        except ValueError:
            flash("Invalid amount. Please enter a valid number.", "danger")
            return redirect(url_for('make_trans'))
        obj.add_transaction(sender,receiver,amount)
        return redirect(url_for('methods'))

    return render_template("make_trans.html",sender=sender)

@app.route('/view_trans',methods=['POST','GET'])
def view_trans():
    user_name = session['username']
    if user_name == "admin":
        my_data = list(collection.find({}))
    else:
        my_data = list(collection.find({"sender_address": session['wallet_address']}))

    for transaction in my_data:
        if isinstance(transaction.get("timestamp"), (float, int)):  
            transaction["timestamp"] = datetime.fromtimestamp(transaction["timestamp"])
        elif isinstance(transaction.get("timestamp"), str):  
            try:
                transaction["timestamp"] = datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass  
    
    if not my_data:
        flash("EMPTY LEDGER")
    

    return render_template("view_trans.html", my_data=my_data)


if __name__=="__main__":
    app.run(debug=True)


