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


class LoginForm(Form):
    username = StringField("Kullanıcı adı")
    password = PasswordField("Parola")

 


app = Flask(__name__)
app.secret_key="gorkem.co"

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


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

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

        sorgu = "Insert into users(name,username,email,password) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,username,email,password,))
        mysql.connection.commit()
        cursor.close()


        flash(message="Başarıyla kayıt oldunuz...", category="success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html", form=form)

@app.route('/login',methods=["GET","POST"])
def login():

    form = LoginForm(request.form)
    if request.method =="POST":
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()

        sorgu = "Select * from users where username = %s"

        result = cursor.execute(sorgu, (username,))

        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            name = data["name"]

            if sha256_crypt.verify(password_entered, real_password):
                flash(message="Başarıyla giriş yaptınız...", category="success")
                session["logged_in"] = True
                session["username"] = username
                session["name"] = name
                return redirect(url_for("index"))
            else:
                flash(message="Parola yanlış...", category="danger")
                return redirect(url_for("login"))

        else:
            flash(message="Kullanıcı bulunamadı", category="danger")
            return redirect(url_for("login"))

    return render_template("login.html",form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash(message="Çıkış yapıldı.", category="success")
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)



