from flask import *
import mysql.connector
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import base64


app=Flask(__name__)

app.secret_key='user' 

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="123",
  database="course_db"
)

mycursor = mydb.cursor(buffered=True)



@app.route('/',methods=['POST','GET'])
def run():
    session['name']=""
    session['role']=""
    session['email']=""
    return "Running"


@app.route('/home',methods=['POST','GET'])
def home():
    return render_template('home.html',name=session['name'],role=session['role'])


@app.route('/register',methods=['POST','GET'])
def register():
    return render_template('register.html',name=session['name'],role=session['role'])

@app.route('/registerf',methods=['POST','GET'])
def registerf():
    session['name']=""
    session['role']=""
    session['email']=""
    r=dict(request.form)
    print(r)
    global mydb
    global mycursor
    if r['pass']!=r['c_pass']:
        return render_template('register.html',u="Password Not Matches")
    mycursor.execute("select email from users")
    l=list(mycursor)
    print(l)
    l=[i[0] for i in l]
    if r['email'] in l: 
         return render_template('register.html',u="Email Exists Try with new Email")
    e=r['email'][::-1]
    if e[0:10]!='moc.liamg@':
        return render_template('register.html',u="Check Your email address")
    s="insert into users(name,userrole,email,password) values(%s,%s,%s,%s)"
    l=[r['name'],r['user_role'],r['email'],r['pass']] 
    print(l) 
    mycursor.execute(s,l)
    mydb.commit()
    return render_template('login.html',u="User Successfully Registered You Can login Now",name=session['name'],role=session['role'])

@app.route('/login',methods=['POST','GET'])
def login():
    session['name']=""
    session['role']=""
    session['email']=""
    return render_template('login.html',name=session['name'])


@app.route('/loginf',methods=['POST','GET'])
def loginf():
    r=dict(request.form)
    email=r['email']
    passw=r['pass']
    e=email[::-1]
    if e[0:10]!='moc.liamg@':
        return render_template('login.html',u="Enter Valid Email")
    s="select * from users where email=%s and password=%s"
    l=[email,passw]
    mycursor.execute(s,l)
    l1=list(mycursor)
    print(l1)
    if(len(l1)<1):
        return render_template('login.html',u="Invalid Login")
    session['email']=email
    session['name']=str(l1[0][2]).upper()
    session['role']=str(l1[0][1]).lower()
    return render_template('home.html',name=session['name'],role=session['role'])

@app.route('/logout',methods=['POST','GET'])
def logout():
    session['name']=""
    session['role']=""
    session['email']=""
    return render_template('home.html',name=session['name'],role=session['role'])

@app.route('/courses',methods=['POST','GET'])
def courses():
    s="select heading,name,bg_img,tot_m,c.c_id  FROM courses c LEFT  JOIN prog p ON c.c_id = p.c_id where p.c_id is null"
    mycursor.execute(s)
    rows=mycursor.fetchall()
    datalist=[]
    for row in rows:
        # email=row[1]
        heading=row[0]
        name=row[1]
        img = base64.b64encode(row[2]).decode('utf-8') if row[2] else None
        tests=row[3]
        c_id=row[4]
        datalist.append(
            {
              'heading':heading,
              'name':name,
              'img':img,
              'progress':'Not Yet Started',
              'tests':tests,
              'c_id':c_id
            }
        )
    return render_template('courses.html',res=datalist,name=session['name'],role=session['role'])

@app.route('/upload',methods=['POST','GET'])
def upload():
    return render_template('upload.html')
    # res=l,name=session['name'],role=session['role']



@app.route('/uploadf',methods=['POST','GET'])
def uploadf():
    r=dict(request.form)
    print(r)
    if 'image' not in request.files:
        return "No image provided", 400
    s="insert into courses(heading,name,bg_img,tot_m) values(%s,%s,%s,%s)"
    img=request.files['image']
    if not img:
        return "no pic uploaded", 400
    img_data=img.read()
    # img_data=base64.b64encode(img_data).decode('utf-8')
    l=[r['hea'],r['name'],img_data,r['num']]
    mycursor.execute(s,l)
    mydb.commit()
    # print(mycursor)
    return render_template('upload.html',u="Successfully Uploaded",name=session['name'],role=session['role'])
     
@app.route('/temp',methods=['POST','GET'])
def temp():
    s="select bg_img from courses where c_id=2"
    mycursor.execute(s)
    row=mycursor.fetchone()[0]
    print(row)
    img=base64.b64encode(row).decode('utf-8')
    return render_template("temp.html",u=img)

@app.route('/enroll/<cid>',methods=['POST','GET'])
def enroll(cid):
    mycursor.execute("select * from prog where c_id=%s",list(cid))
    if(len(list(mycursor))==0):
            s="insert into prog (email,c_id,mod_c) values(%s,%s,%s)"
            l=[session['email'],cid,0]
            mycursor.execute(s,l)
            mydb.commit()

    # my subcription code
    s="select heading,name,bg_img,tot_m,c.c_id  FROM courses c INNER  JOIN prog p ON c.c_id = p.c_id"
    mycursor.execute(s)
    rows=mycursor.fetchall()
    # print("hurrey",rows)
    datalist=[]
    for row in rows:
        # email=row[1]
        heading=row[0]
        name=row[1]
        img = base64.b64encode(row[2]).decode('utf-8') if row[2] else None
        tests=row[3]
        c_id=row[4]
        s1="select mod_c from prog where c_id=%s and email=%s"
        m=[row[4],session['email']]
        mycursor.execute(s1,m)
        mod_c=mycursor.fetchone()[0]
        # print("hoho",list(mycursor)[0],mod_c)
        tol_m=row[3]
        if(mod_c==tol_m):
            prog='Completed'
        else:
            prog='Inprogress'
        prog_bar=mod_c*tol_m/100
        datalist.append(
            {
              'heading':heading,
              'name':name,
              'img':img,
              'progress':prog,
              'tests':tests,
              'c_id':c_id,
              'prog_bar':prog_bar
            }
        )
    # img_base64_list = [base64.b64encode(row[0]).decode('utf-8') for row in rows]
    return render_template('courses.html',res=datalist,name=session['name'],role=session['role'],u="Successfully Subscribed",to='mysub')
    
@app.route('/unenroll/<cid>',methods=['POST','GET'])
def unenroll(cid):
    s="delete from prog where email=%s and c_id=%s"
    l=[session['email'],cid]
    mycursor.execute(s,l)
    mydb.commit()

    # my subscription code
    s="select heading,name,bg_img,tot_m,c.c_id  FROM courses c INNER  JOIN prog p ON c.c_id = p.c_id"
    mycursor.execute(s)
    rows=mycursor.fetchall()
    # print("hurrey",rows)
    datalist=[]
    for row in rows:
        # email=row[1]
        heading=row[0]
        name=row[1]
        img = base64.b64encode(row[2]).decode('utf-8') if row[2] else None
        tests=row[3]
        c_id=row[4]
        s1="select mod_c from prog where c_id=%s and email=%s"
        m=[row[4],session['email']]
        mycursor.execute(s1,m)
        mod_c=mycursor.fetchone()[0]
        # print("hoho",list(mycursor)[0],mod_c)
        tol_m=row[3]
        if(mod_c==tol_m):
            prog='Completed'
        else:
            prog='Inprogress'
        prog_bar=mod_c*tol_m/100
        datalist.append(
            {
              'heading':heading,
              'name':name,
              'img':img,
              'progress':prog,
              'tests':tests,
              'c_id':c_id,
              'prog_bar':prog_bar
            }
        )
    # img_base64_list = [base64.b64encode(row[0]).decode('utf-8') for row in rows]
    return render_template('courses.html',res=datalist,name=session['name'],role=session['role'],u="Successfully UnSubscribbed",to='mysub')
   
      
@app.route('/mysub',methods=['POST','GET'])
def mysub():
    s="select heading,name,bg_img,tot_m,c.c_id  FROM courses c INNER  JOIN prog p ON c.c_id = p.c_id"
    mycursor.execute(s)
    rows=mycursor.fetchall()
    # print("hurrey",rows)
    datalist=[]
    for row in rows:
        # email=row[1]
        heading=row[0]
        name=row[1]
        img = base64.b64encode(row[2]).decode('utf-8') if row[2] else None
        tests=row[3]
        c_id=row[4]
        s1="select mod_c from prog where c_id=%s and email=%s"
        m=[row[4],session['email']]
        mycursor.execute(s1,m)
        mod_c=mycursor.fetchone()[0]
        # print("hoho",list(mycursor)[0],mod_c)
        tol_m=row[3]
        if(mod_c==tol_m):
            prog='Completed'
        else:
            prog='Inprogress'
        prog_bar=mod_c*tol_m/100
        datalist.append(
            {
              'heading':heading,
              'name':name,
              'img':img,
              'progress':prog,
              'tests':tests,
              'c_id':c_id,
              'prog_bar':prog_bar
            }
        )
    # img_base64_list = [base64.b64encode(row[0]).decode('utf-8') for row in rows]
    return render_template('courses.html',res=datalist,name=session['name'],role=session['role'],to='mysub')
   





mydb.commit()


if __name__ == '__main__':
    try:
        app.run(debug=True)
    except KeyboardInterrupt:  # Catch Ctrl+C interrupt
        # Clear session variables when program stops
       session['name']=""
       session['role']=""
       session['email']=""



