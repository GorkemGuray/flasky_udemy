from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt

#Kullanıcı kayıt formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.length(min =4 , max=25)])
    username = StringField("Kullanıcı Adı",validators=[validators.length(min =5 , max=35)])
    email = StringField("Email Adresi",validators=[validators.Email(message="Lütfen geçerli bir email adresi girin")])
    password = PasswordField("Parola:",validators=[
        validators.DataRequired(message="Lütfen bir parola belirieyin"),
        validators.EqualTo(fieldname = "confirm", message="Parolanız uyuşmuyor")
    ])
    confirm = PasswordField("Parola Doğrula")

 


app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "clas1070"
app.config["MYSQL_DB"] = "grkm_blg"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)



@app.route('/')
def index():
    articles = [
        {"id":1, "title":"Deneme1", "content":"Deneme 1 içerik"},
        {"id":2, "title":"Deneme2", "content":"Deneme 2 içerik"},
        {"id":3, "title":"Deneme3", "content":"Deneme 3 içerik"}
    ]
    return render_template("index.html", articles=articles)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/article/<string:id>')
def article(id):
    return "Article id:" + id

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)

    if request.method =="POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()

        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,username,email,password,))
        mysql.connection.commit()
        cursor.close()



        return redirect(url_for("index"))
    else:
        return render_template("register.html", form=form)
    


if __name__ == '__main__':
    app.run(debug=True)



