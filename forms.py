from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,IntegerField,FloatField,FileField, SelectField, validators
from wtforms.validators import DataRequired,  Length,NumberRange,ValidationError
from flask_wtf.file import FileAllowed






class SignUpForm(FlaskForm):
    first_name = StringField("First name",validators=[DataRequired()])
    last_name = StringField("Second name",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    city = SelectField("City where you work",choices=[],validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired(),Length(min=8)])
    password2 = PasswordField("Confirm password",validators=[DataRequired(),Length(min=8)])

    submit = SubmitField("Submit")

class LogInForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])

    submit = SubmitField("Submit")

class UpdatePassword(FlaskForm):
    oldpassword = PasswordField("Old Password",validators=[DataRequired(),Length(min=8)])

    password = PasswordField("New Password",validators=[DataRequired(),Length(min=8)])
    password2 = PasswordField("Confirm New Password",validators=[DataRequired(),Length(min=8)])
    submit = SubmitField("Submit")

class AddSuppliers(FlaskForm):
    first_name = StringField("First name",validators=[DataRequired()])
    last_name = StringField("Second name",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    phone = StringField("Phone Number",validators=[DataRequired()])
    city = StringField("City",validators=[DataRequired()])

    submit = SubmitField("Submit")

class AddItemForm(FlaskForm):
    def validate_with_params(x, name):
        def decorator(func):
            def wrapper(form, field, x=x, name=name):
                return func(form, field, x=x, name=name)
            return wrapper
        return decorator

    @validate_with_params(x=5, name="Item Model ID")
    def validate_code(form, field, x=None, name=None):
        if not field.data.isdigit() or len(field.data) != x:
            raise ValidationError(f'{name} must be exactly {x} digits.')
        
    def positive_number_check(form, field):
        if field.data <= 0:
            raise ValidationError('Amount must be a positive number.')
        
    item_model = StringField("Item Model",validators=[DataRequired()])

    item_model_id = StringField("Item Model ID", validators=[validate_code])
    producing_country_id = StringField('Producing Country ID', validators=[validate_with_params(3, 'Producing Country ID')(validate_code)])
    manufacturer_id = StringField("Manufacturer ID", validators=[validate_with_params(4, "Manufacturer ID")(validate_code)])
   
    category = SelectField("Category",choices=[],validators=[DataRequired()])
    price = FloatField("Price In Usd",validators=[validators.NumberRange(min=0, message="Price must be a positive number.")])
    producing_country = StringField("Producing Country",validators=[DataRequired()])
    colour = StringField("Colour",validators=[DataRequired()])
    manufacturer = StringField("Manufacturer",validators=[DataRequired()])
    amount = IntegerField("Amount", validators=[DataRequired(), positive_number_check])
    place = StringField("Place",validators=[DataRequired()])
    img = FileField("Image", validators=[FileAllowed(['jpg','jpeg','png'])])

    submit = SubmitField("Submit")

class Amount(FlaskForm):    
    amount = IntegerField("Amount", validators=[DataRequired()])

    submit = SubmitField("Submit")

class SearchForm(FlaskForm):
    searched = StringField("Searched",validators=[DataRequired()])

    submit = SubmitField("Submit")

class Departure(FlaskForm):

        
    city_to = SelectField("City to Send",choices=[],validators=[DataRequired()])
    amountD = IntegerField("Amount for departure", validators=[DataRequired()])

    submit = SubmitField("Submit")

class AcceptTheDeparture(FlaskForm):

    place = StringField("Place For The Item In The Warehouse ",validators=[DataRequired()])

    submit = SubmitField("Submit")

class AddCategory(FlaskForm):
    name = StringField("Category Name",validators=[DataRequired()])
    category_img = FileField("Image", validators=[FileAllowed(['jpg','jpeg','png'])])

    submit = SubmitField("Submit")