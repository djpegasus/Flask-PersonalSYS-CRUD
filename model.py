from wtforms import (Form, StringField, PasswordField,
                     TelField, RadioField, validators)
from wtforms.validators import InputRequired

class LoginForm(Form):
    username = StringField("Kullanıcı Adı", validators=[validators.DataRequired()])
    password = PasswordField("Pasola", validators=[validators.DataRequired()])
    
class RegisterForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola", validators=[validators.DataRequired(message="Bir Parola Belirleyiniz"),
                                                    validators.EqualTo("confirm", message="Parola Uyuşmuyor")])
    confirm = PasswordField("Parola Doğrula")

class PersonelForm(Form):
    name = StringField("Personel Adı")
    surname = StringField("Personel Soyadı")
    id_no = StringField("Kimlik Numarası", validators=[validators.Length(min=11, max=11, message="Geçerli Kimlik Numarası Giriniz.")])
    unvan = StringField("Ünvan")
    dept = StringField("Departman")
    date = StringField("Başlangıç Tarihi")
    tel = TelField("Telefon Numarası", validators=[validators.DataRequired(message="Lütfen Başında sıfır olmadan Giriniz. (5XX XXX XXXX)")])
    email = StringField("E-posta Adresi", validators=[validators.email(message="Lütfen geçerli bir email adresi girin.")])
    username = StringField("Kullanıcı Kodu", validators=[validators.DataRequired()])
    yetki_code = RadioField('Dept', choices=[
        (1,'Yönetici'), (2,'Satış'), (3,'Satınalma')],
         coerce=int, validators=[InputRequired(message="Bir Seçim Yapını")])
    aktif = StringField("Aktif/Pasif", default="X")
        
class UpdatePass(Form):
    password = PasswordField("Parola", validators=[
        validators.DataRequired(message="Bir Parola Belirleyiniz"),
        validators.EqualTo("confirm", message="Parola Uyuşmuyor")])
    confirm = PasswordField("Parola Doğrula")
    

class UpdatePersonal(Form):
    surname = StringField("Personel Soyadı")
    unvan = StringField("Ünvan")
    dept = StringField("Departman")
    tel = TelField("Telefon Numarası", validators=[validators.DataRequired(message="Lütfen Başında sıfır olmadan Giriniz. (5XX XXX XXXX)")])
    email = StringField("E-posta Adresi", validators=[validators.email(message="Lütfen geçerli bir email adresi girin.")])