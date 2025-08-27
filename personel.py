from flask import Flask, render_template, redirect, request, url_for, flash, session, jsonify, make_response
from flask_mysqldb import MySQL
from model import RegisterForm, LoginForm, PersonelForm, UpdatePass, UpdatePersonal
from passlib.hash import pbkdf2_sha256
from functools import wraps
from config import Config

app = Flask(__name__, template_folder="mfy-content", static_folder="assets")
app.config.from_object(Config)
app.secret_key = "192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf"
mysql = MySQL(app)

# Login control decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın...", "danger")
            return redirect(url_for("index"))
    return decorated_function

# Register Test 
@app.route("/register", methods = ["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        password = pbkdf2_sha256.encrypt(form.password.data)
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s,%s)", (username, password))
        mysql.connection.commit()
        cursor.close()
        flash("Kayıt Başarı ile Yapılmıştır.", "success")
        return redirect(url_for("index"))
    else:
        flash("Girdiğiniz Parola Uyuşmuyor...", "danger")
    return render_template("register.html", form=form)

# Logout Fonksiyonu 
@app.route("/logout")
def logout():
    session.clear()
    flash("Güvenli Çıkış Yapıldı.", "success")
    return redirect(url_for("index"))

# Login Fonksiyonu
@app.route("/", methods = ["GET", "POST"])
def index():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        enter_pass = form.password.data
        cursor = mysql.connection.cursor()
        result = cursor.execute("SELECT * FROM users u JOIN personel p ON u.username = p.username WHERE u.username = %s", (username,))
        if result > 0:
            data = cursor.fetchone()
            control = data["loginControl"]
            real_pass = data["password"]
            auth = data["yetki"]
            if pbkdf2_sha256.verify(enter_pass, real_pass) and control == 0:
                flash("Şifre sıfırlama ekranı Giriş Yaptınız", "success")
                session["username"] = username
                session["loginControl"] = control
                return redirect(url_for("newPass"))
            elif pbkdf2_sha256.verify(enter_pass, real_pass) and control !=0:
                if (auth == 2 or auth == 3):
                    session["logged_in"] = True
                    session["username"]= username
                    session["yetki"] = auth
                    session["name"] = data["name"]
                    session["surname"] = data["surname"]
                    session["id_no"] = data["id_no"]
                    session["tel"] = data["tel"]
                    session["email"] = data["email"]
                    session["unvan"] = data["unvan"]
                    session["dept"] = data["dept"]
                    flash("Kullanıcı Olarak Giriş Yaptınız.", "success")
                    return redirect(url_for("perPanel"))
                else:
                    session["logged_in"] = True
                    session["username"]= username
                    session["yetki"] = auth
                    session["name"] = data["name"]
                    session["surname"] = data["surname"]
                    session["id_no"] = data["id_no"]
                    session["tel"] = data["tel"]
                    session["email"] = data["email"]
                    session["unvan"] = data["unvan"]
                    session["dept"] = data["dept"]
                    flash("Yönentici Olarak Giriş Yaptınız.", "success")
                    return redirect(url_for("dashboard"))
            else:
                flash("Kullanıcı veya Parola Hatalı", "danger")
                return redirect(url_for("index"))
        else:
            flash("Girdiğiniz Kullanıcı Bulunamadı.", "danger")
            return redirect(url_for("index"))
    return render_template("index.html", form=form)

# İlk Giriş Parola Sıfırlama Fonksiyonu
@app.route("/newPass", methods = ["GET", "POST"])
@login_required
def newPass():
    form = UpdatePass(request.form)
    if request.method == "POST" and form.validate():
        password = pbkdf2_sha256.encrypt(form.password.data)
        cursor = mysql.connection.cursor()
        result = cursor.execute("select * from users where username = %s",(session["username"],))
        if result > 0:
            data = cursor.fetchone()
            control = data["loginControl"]
            control = 1
            cursor.execute ("update users set password= %s, loginControl = %s where username=%s", (password, control, session["username"]))
            mysql.connection.commit()
            cursor.close()
            flash("Parolanız Güncellendi", "success")
            return redirect(url_for("index"))
        else:
            flash("Parolanız uyuşmuyor", "danger")
            return redirect(url_for("newPass"))
    return render_template("newPass.html", form=form)

# Dashboard Fonksiyonu
@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()
    select = cursor.execute("select * from personel ")
    if select > 0:
        personel = cursor.fetchall()
        return render_template("dashboard.html", personel=personel)
    else:    
        return render_template("dashboard.html")

# Personel Kayıt Fonksiyonu
@app.route("/perKayit", methods = ["GET", "POST"])
@login_required
def perKayit():
    form = PersonelForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        surname = form.surname.data
        id_no = form.id_no.data
        unvan = form.unvan.data
        dept = form.dept.data
        date = form.date.data
        tel = form.tel.data
        email = form.email.data
        username = form.username.data
        pkod = "PK" + str(username)
        yetki = form.yetki_code.data
        aktif = form.aktif.default
        cursor = mysql.connection.cursor()
        query ="INSERT INTO personel (name, surname, id_no, unvan, dept, date, tel, email, username, yetki,aktif) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query,(name, surname, id_no, unvan, dept, date, tel, email, pkod, yetki,aktif))
        mysql.connection.commit()
        cursor.close()
        username = pkod
        password = pbkdf2_sha256.encrypt("1")
        loginControl = 0
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password,loginControl, yetki,aktif) VALUES (%s,%s,%s,%s,%s)", (username,password,loginControl,yetki,aktif))
        mysql.connection.commit()
        cursor.close() 
        flash("Kayıt Başarı ile Yapılmıştır.", "success")
        return redirect(url_for("dashboard"))
    return render_template("perKayit.html", form=form)

@app.route("/perList")
@login_required
def perList():
    cursor = mysql.connection.cursor()
    select = cursor.execute("select * from personel where yetki > 1")
    if select > 0:
        personel = cursor.fetchall()
        return render_template("perList.html", personel=personel)
    else:
        flash("Personel Kaydı Bulunamamıştır.", "success")
        return render_template("perList.html")

@app.route("/perUpd/<string:username>", methods=["GET", "POST"])
def update_personel(username):
    form = UpdatePersonal(request.form)
    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT * FROM personel WHERE username = %s", (username,))
    if result > 0:
        personel = cursor.fetchone()
        if request.method == "POST" and form.validate():
            surname = form.surname.data
            unvan = form.unvan.data
            dept = form.dept.data
            tel = form.tel.data
            email = form.email.data
            cursor.execute("UPDATE personel SET surname = %s, unvan =%s, dept=%s, tel = %s, email=%s  WHERE username = %s", (surname, unvan, dept, tel, email, username))
            mysql.connection.commit()
            cursor.close()
            flash("Personel bilgileri güncellendi", "success")
            return redirect(url_for("perList"))
        form.surname.data = personel["surname"]
        form.unvan.data = personel["unvan"]
        form.dept.data = personel["dept"]
        form.tel.data = personel["tel"]
        form.email.data = personel["email"]
        return render_template("perUpd.html", form=form, personel=personel)
    else:
        flash("Personel bulunamadı", "danger")
        return redirect(url_for("perList"))

@app.route("/perStatus", methods=["GET", "POST"])
@login_required
def perStatus():
    cursor = mysql.connection.cursor()
    select = cursor.execute("select * from personel where yetki > 1")
    if select > 0:
        personel = cursor.fetchall()
        return render_template("perStatus.html", personel=personel)
    else:
        flash("Personel Kaydı Bulunamamıştır.", "danger")
        return render_template("perStatus.html")

@app.route("/update_status/<int:id>", methods=["POST"])
@login_required
def update_status(id):
    aktif = request.json.get('aktif')
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE personel SET aktif = %s WHERE id = %s", (aktif, id))
    cursor.execute("UPDATE users u JOIN personel p ON u.username = p.username SET u.aktif = %s WHERE p.id = %s", (aktif, id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"success": True})

@app.route("/report")
def pdfReport():
    return render_template("report.html")
    
@app.route("/perPanel")
def perPanel():
    return render_template("perPanel.html")


if __name__ == "__main__":
    app.run(debug=True)