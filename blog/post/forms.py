from flask_wtf import FlaskForm
from flask_wtf.file import file_allowed
from wtforms import StringField, TextAreaField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Статья', validators=[DataRequired()])
    category = SelectField('Категория',choices=['Политика','Экономика', 'Спорт', 'Программирование', 'Разное'])
    tag_form = StringField('Тэг')
    picture = FileField('Изображение (jpg, png)', validators=[file_allowed(['jpg','png'])])
    submit = SubmitField('Опубликовать')

class PostUpdateForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Статья', validators=[DataRequired()])
    category = SelectField('Категория', choices=['Политика', 'Экономика', 'Спорт', 'Программирование', 'Разное'])
    picture = FileField('Изображение (jpg, png)', validators=[file_allowed(['jpg','png'])])
    submit = SubmitField('Опубликовать')

class CommentUpdateForm(FlaskForm):
    body = StringField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')
