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
  database="course"
)

mycursor = mydb.cursor(buffered=True)

img_prof=""


@app.route('/',methods=['POST','GET'])
def run():
    session['name']=""
    session['role']=""
    session['email']=""
    global img_prof
    img_prof=""
    return  """
    <html>
    <head>
        <title>Home Page</title>
    </head>
    <body>
        <h1>Running</h1>
        <p>Click <a href="/home">here</a> to go to the home page.</p>
    </body>
    </html>
    """




@app.route('/register',methods=['POST','GET'])
def register():
    session['name']=""
    session['role']=""
    session['email']=""
    global img_prof
    img_prof=""
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
    s="insert into users(name,userrole,email,password,img) values(%s,%s,%s,%s,%s)"
    img=request.files['image']
    if not img:
        return "no pic uploaded", 400
    img_data=img.read()
    l=[r['name'],r['user_role'],r['email'],r['pass'],img_data] 
    # print(l) 
    mycursor.execute(s,l)
    mydb.commit()
    return render_template('login.html',u="User Successfully Registered You Can login Now",name=session['name'],role=session['role'])

@app.route('/login',methods=['POST','GET'])
def login():
    session['name']=""
    session['role']=""
    session['email']=""
    global img_prof
    img_prof=""
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
    # print(l1)
    if(len(l1)<1):
        return render_template('login.html',u="Invalid Login")
    session['email']=email
    session['name']=str(l1[0][2]).upper()
    session['role']=str(l1[0][1]).lower()
    global img_prof
    img_prof = base64.b64encode(l1[0][5]).decode('utf-8') if l1[0][5] else None
    # session['img']=img
    # print(session['img'])
    return render_template('home.html',name=session['name'],role=session['role'],to="home",img=img_prof)

@app.route('/home',methods=['POST','GET'])
def home():
    try:
        return render_template('home.html',name=session['name'],role=session['role'],to="home",img=img_prof)
    except :
        return render_template('home.html',name="",role="",to="home")


@app.route('/uploadm',methods=['POST','GET'])
def uploadm():
    return render_template('upload.html',name=session['name'],role=session['role'],to="module",img=img_prof)


@app.route('/uploadmf',methods=['POST','GET'])
def uploadmf():
    r=dict(request.form)
    hea=r['hea']
    mycursor.execute("select * from module where m_name=%s",(hea,))
    if(len(list(mycursor)) > 0):
            return render_template('upload.html',name=session['name'],role=session['role'],u="Heading Already Exists",to="module",img=img_prof)
    
    s="insert into module(email,m_name,doc,exam,reference) values(%s,%s,%s,%s,%s)"
    page = request.files['page']
    page_data = page.read()
    exam = request.files['exam']
    exam_data = exam.read()
    l=[session['email'],r['hea'],page_data,exam_data,r['reference']]
    mycursor.execute(s,l)
    mydb.commit()
    return render_template('upload.html',name=session['name'],role=session['role'],u="Module Added",to="module",img=img_prof)


@app.route('/upload',methods=['POST','GET'])
def upload():
    s="select m_name from module where email=%s"
    mycursor.execute(s,(session['email'],))
    m=list(mycursor)
    return render_template('upload.html',mod=m,to="course",name=session['name'],role=session['role'],img=img_prof)
    # res=l,name=session['name'],role=session['role']


@app.route('/uploadf',methods=['POST','GET'])
def uploadf():
    r=dict(request.form)
    print(r)
    if 'image' not in request.files:
        return "No image provided", 400
    s="insert into courses(heading,name,bg_img,tot_m,m_name) values(%s,%s,%s,%s,%s)"
    img=request.files['image']
    if not img:
        return "no pic uploaded", 400
    img_data=img.read()
    # img_data=base64.b64encode(img_data).decode('utf-8')
    l=[r['hea'],r['name'],img_data,r['num'],r['mod']]
    mycursor.execute(s,l)
    mydb.commit()
    # print(mycursor)

    s="select m_name from module where email=%s"
    mycursor.execute(s,(session['email'],))
    m=list(mycursor)
    return render_template('upload.html',u="Successfully Uploaded",mod=m,to="course",name=session['name'],role=session['role'],img=img_prof)
    

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
    return render_template('courses.html',res=datalist,name=session['name'],role=session['role'],to='mycou',img=img_prof)


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
        prog_bar=int(mod_c/tol_m*100)
        print(prog_bar)
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
    return render_template('courses.html',res=datalist,name=session['name'],role=session['role'],u="Successfully Subscribed",to='mysub',img=img_prof)
    
     
@app.route('/mysub',methods=['POST','GET'])
def mysub():
    s="select heading,name,bg_img,tot_m,c.c_id FROM courses c INNER  JOIN prog p ON c.c_id = p.c_id"
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
        try:
            mod_c=mycursor.fetchone()[0]
        except:
            mod_c=0
        # print("hoho",list(mycursor)[0],mod_c)
        tol_m=row[3]
        if(mod_c==tol_m):
            prog='Completed'
        else:
            prog='Inprogress'
        prog_bar=int(mod_c/tol_m*100)
        print(prog_bar)
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
    return render_template('courses.html',res=datalist,name=session['name'],role=session['role'],to='mysub',img=img_prof)
   

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
        try:
            mod_c=mycursor.fetchone()[0]
        except:
            mod_c=0
        # print("hoho",list(mycursor)[0],mod_c)
        tol_m=row[3]
        if(mod_c==tol_m):
            prog='Completed'
        else:
            prog='Inprogress'
        prog_bar=mod_c/tol_m*100
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
    return render_template('courses.html',res=datalist,name=session['name'],role=session['role'],u="Successfully UnSubscribbed",to='mysub',img=img_prof)
   
 

@app.route('/start/<cid>',methods=['POST','GET'])
def start(cid):
    s="select name,m_name from courses where c_id=%s"
    mycursor.execute(s,(cid,))
    l=mycursor.fetchone()
    session['m_name']=l[1]
    session['c_id']=cid
    # print(l)
    return render_template('home.html',name=session['name'],role=session['role'],to='quick',l=l,img=img_prof)


@app.route('/startf/<n>',methods=['POST','GET'])
def startf(n):
    mycursor.execute("select tot_m from courses where c_id=%s",(session['c_id'],))
    l=mycursor.fetchone()[0]
    print("l is ",l)
    mycursor.execute("UPDATE prog SET mod_c = mod_c + 1 WHERE email = %s AND c_id = %s AND mod_c < %s", (session['email'], session['c_id'],l))
    if(n=='1'):
        s="select doc from module where m_name=%s"
        mycursor.execute(s,(session['m_name'],))
        l=mycursor.fetchone()[0]
        return render_template('temp.html',name=session['name'],role=session['role'],to='mod',l=l,img=img_prof)
    if(n=='2'):
        s="select exam from module where m_name=%s"
        mycursor.execute(s,(session['m_name'],))
        l=mycursor.fetchone()[0]
        return render_template('temp.html',name=session['name'],role=session['role'],to='mod',l=l,img=img_prof)
    if(n=='3'):
        s="select reference from module where m_name=%s"
        mycursor.execute(s,(session['m_name'],))
        l=mycursor.fetchone()[0]
        if l:
            # Check if the URL includes a scheme, if not, add one
            if not l.startswith(('http://', 'https://')):
                l = 'http://' + l
            return redirect(l)
        else:
            return "No reference found for this module."
            # return render_template('temp.html',name=session['name'],role=session['role'],to='ref',l=l,img=img_prof)

       

    


@app.route('/delete',methods=['POST','GET'])
def delete():
    s="select c.heading,c.name,c.bg_img,c.tot_m,c.c_id,c.m_name FROM courses c JOIN module m ON c.m_name = m.m_name WHERE m.email = %s"
    mycursor.execute(s, (session['email'],) )
    rows=mycursor.fetchall()
    datalist=[]
    for row in rows:
        # email=row[1]
        heading=row[0]
        name=row[1]
        img = base64.b64encode(row[2]).decode('utf-8') if row[2] else None
        tests=row[3]
        c_id=row[4]
        m_name=row[5]
        
        datalist.append( 
            {
              'heading':heading,
              'name':name,
              'img':img,
              'progress':'Not Yet Started',
              'tests':tests,
              'c_id':c_id,
              'm_name':m_name
            }
        )
    return render_template('courses.html',res=datalist,name=session['name'],role=session['role'],to='delcou',img=img_prof)



@app.route('/deletef/<cid>',methods=['POST','GET'])
def deletef(cid):
        s="delete from prog where c_id=%s"
        s1="delete from courses where c_id=%s"
        mycursor.execute(s,(cid,))
        mycursor.execute(s1,(cid,))
        mydb.commit()

        s="select c.heading,c.name,c.bg_img,c.tot_m,c.c_id,c.m_name FROM courses c JOIN module m ON c.m_name = m.m_name WHERE m.email = %s"
        mycursor.execute(s, (session['email'],) )
        rows=mycursor.fetchall()
        datalist=[]
        for row in rows:
                # email=row[1]
                heading=row[0]
                name=row[1]
                img = base64.b64encode(row[2]).decode('utf-8') if row[2] else None
                tests=row[3]
                c_id=row[4]
                m_name=row[5]
                
                datalist.append(
                    {
                    'heading':heading,
                    'name':name,
                    'img':img,
                    'progress':'Not Yet Started',
                    'tests':tests,
                    'c_id':c_id,
                    'm_name':m_name
                    }
                )
        return render_template('courses.html',res=datalist,name=session['name'],role=session['role'],to='delcou',img=img_prof)





@app.route('/contact',methods=['POST','GET'])
def contact():
        return render_template('home.html',name=session['name'],role=session['role'],to="contact",img=img_prof)

@app.route('/about',methods=['POST','GET'])
def about():
    return render_template('home.html',name=session['name'],role=session['role'],to="about",img=img_prof)

@app.route('/profile',methods=['POST','GET'])
def profile():
    mycursor.execute("select count(*) from module where email=%s",(session['email'],))
    m_created=mycursor.fetchone()[0]
    mycursor.execute("select count(*) from prog where email=%s",(session['email'],))
    c_enroll=mycursor.fetchone()[0]
    s=" SELECT count(*) FROM courses c JOIN module m ON c.m_name = m.m_name WHERE m.email = %s"
    mycursor.execute(s,(session['email'],))
    c_created=mycursor.fetchone()[0]
    l=[m_created,c_enroll,c_created]
    print(l)
    return render_template('home.html',name=session['name'],role=session['role'],l=l,to="profile",img=img_prof)


@app.route('/logout',methods=['POST','GET'])
def logout():
    session['name']=""
    session['role']=""
    session['email']=""
    img_prof=""
    return render_template('home.html',name=session['name'],to="home",role=session['role'])  


@app.route('/temp',methods=['POST','GET'])
def temp():
    s="select bg_img from courses where c_id=2"
    mycursor.execute(s)
    row=mycursor.fetchone()[0]
    print(row)
    img=base64.b64encode(row).decode('utf-8')
    return render_template("temp.html",u=img)

mydb.commit()

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except KeyboardInterrupt:  # Catch Ctrl+C interrupt
        # Clear session variables when program stops
       session['name']=""
       session['role']=""
       session['email']=""



