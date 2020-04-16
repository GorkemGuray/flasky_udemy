from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

#Kullanıcı giris decorator'ı
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash(message="Bu sayfayı görmeye yetkiniz yok...", category="warning")
            return redirect(url_for("login"))
    return decorated_function


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

#Kullanıcı giriş formu
class LoginForm(Form):
    username = StringField("Kullanıcı adı")
    password = PasswordField("Parola")

#Makale ekleme formu
class ArticleForm(Form):
    title = StringField("Makale Başlığı", validators=[validators.length(max=255)])
    content = TextAreaField("Makale", validators=[validators.length(min=10)])

 


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
    return render_template("index.html")
#Hakkımda sayfası
@app.route('/about')
def about():
    return render_template("about.html")

#Makaleler sayfası
@app.route('/articles')
def articles():
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles"
    result = cursor.execute(sorgu)

    if result > 0:
        articles = cursor.fetchall()
        return render_template("articles.html",articles = articles)
    else:
        return render_template("articles.html")

#Makale detay sayfası
@app.route('/article/<string:id>')
def single_article(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * from articles where id = %s"

    result = cursor.execute(sorgu, (id,))

    if result > 0:
        article = cursor.fetchone()
        return render_template("single_article.html", article=article)
    else:
        return render_template("single_article.html")
    

#Kontrol Paneli
@app.route('/dashboard')
@login_required
def dashboard():
    cursor = mysql.connection.cursor()
    sorgu = "Select * from articles where author = %s"
    result = cursor.execute(sorgu,(session["username"],))

    if result > 0:
        articles = cursor.fetchall()
        return render_template('dashboard.html',articles=articles)
    else:
        return render_template("dashboard.html")
#Makaleler
@app.route('/article/<string:id>')
def article(id):
    return "Article id:" + id

#Kullanıcı kayıt sayfası
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

#Kullanıcı giriş sayfası
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

#Kullanıcı çıkış sayfası
@app.route('/logout')
def logout():
    session.clear()
    flash(message="Çıkış yapıldı.", category="success")
    return redirect(url_for("index"))


#Makale ekleme
@app.route('/addarticle', methods=["GET", "POST"])
@login_required
def addarticle():
    form = ArticleForm(request.form)

    if request.method =="POST" and form.validate():
        title = form.title.data
        content = form.content.data

        cursor = mysql.connection.cursor()
        sorgu = "Insert into articles (title,author,content) values(%s,%s,%s)"
        cursor.execute(sorgu,(title, session["username"],content,))
        mysql.connection.commit()
        cursor.close()

        flash(message="Makale başarıyla eklendi...", category="success")
        return redirect(url_for("dashboard"))


    return render_template("addarticle.html",form=form)

#Makale Silme
@app.route('/delete/<string:id>')
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * from articles where author = %s and id= %s"
    sorgu2 = "Delete from articles where id = %s"

    result = cursor.execute(sorgu,(session["username"],id))

    if result>0:
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        cursor.close()
        flash(message="{} \'nolu makale başarıyla silinidi...".format(id),category="success")
        return redirect(url_for("dashboard"))
    else:
        flash(message="Böyle bir makale yok veya bu işleme yetkiniz yok.", category="danger")
        return redirect(url_for("index"))

#Makale Güncelleme
@app.route("/edit/<string:id>",methods=["GET","POST"])
@login_required
def edit(id):
    if request.method =="GET":
        cursor = mysql.connection.cursor()
        sorgu = "Select * from articles where id = %s and author = %s"

        result = cursor.execute(sorgu, (id,session["username"]))

        if result ==0:
            cursor.close()
            flash(message="Böyle bir makale yok veya bu işleme yetkiniz yok.", category="danger")
            return redirect(url_for("index"))
        else:
            article = cursor.fetchone()
            cursor.close()
            form = ArticleForm()

            form.title.data=article["title"]
            form.content.data=article["content"]
            return render_template("edit.html",form=form)
    elif request.method =="POST":
        form = ArticleForm(request.form)
        newTitle = form.title.data
        newContent = form.content.data

        sorgu = "Update articles Set title= %s, content= %s where id= %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu,(newTitle,newContent,id))
        mysql.connection.commit()
        cursor.close()

        flash(message="{} \'nolu makale başarıyla güncellendi...".format(id), category="success")
        return redirect(url_for("dashboard"))


if __name__ == '__main__':
    app.run(debug=True)



