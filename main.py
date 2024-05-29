from flask import request, jsonify, render_template,Flask,flash, redirect, url_for, session
from config import app, db
from models import Users, Items, Warehouses, Items_actions,Items_departure_temp,Categories, Suppliers, Customers
from sqlalchemy import or_, select, not_, and_
from sqlalchemy.orm import aliased
from forms import SignUpForm, LogInForm, AddItemForm, SearchForm, Amount, Departure, AcceptTheDeparture, AddCategory, UpdatePassword, AddSuppliers
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash 
from werkzeug.utils import secure_filename
import uuid as uuid
import os
import barcode
from barcode import EAN13
from barcode.writer import ImageWriter
from functions import *



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/main', methods = ['GET','POST'])
@login_required
def main():
    form = AddCategory()
    category_query = db.session.query(
            Categories.name,
            Categories.category_img)
    
    categories = category_query.all()

    

    if request.method == "POST": 
        if form.validate_on_submit():
            name = request.form['name']
            existing_category = Categories.query.filter_by(name=name).first()
            if existing_category is None:
                pic = request.files['category_img']
                if pic:
                    pic_filename = secure_filename(pic.filename)
                    pic_name = str(uuid.uuid1()) + "_" + pic_filename
                    pic.save(os.path.join(app.root_path, 'static', 'categories', pic_name))
                else:
                    pic_name = None
                try: 
                    
                    category = Categories(
                                    name=name,
                                    category_img=pic_name,
                                )
                    db.session.add(category)
                    db.session.commit()
                    flash("You Have Successfully Created A Category")
                except Exception as e:
                        flash(f"Error! Looks like there was a problem: {str(e)}")
            else: flash('A Category With This Name Already Exists')
            
    return render_template("main.html", form = form, categories = categories)

@app.route('/main/category_manegment', methods = ['GET','POST'])
@login_required
def category_manegment():
    form = AddCategory()
    category_query = db.session.query(
            Categories.name,
            Categories.category_img)
    
    categories = category_query.all()
    if request.method == "POST": 
        if form.validate_on_submit():
            name = request.form['name']
            existing_category = Categories.query.filter_by(name=name).first()
            if existing_category is None:
                pic = request.files['category_img']
                if pic:
                    pic_filename = secure_filename(pic.filename)
                    pic_name = str(uuid.uuid1()) + "_" + pic_filename
                    pic.save(os.path.join(app.root_path, 'static', 'categories', pic_name))
                else:
                    pic_name = None
                try: 
                    
                    category = Categories(
                                    name=name,
                                    category_img=pic_name,
                                )
                    db.session.add(category)
                    db.session.commit()
                    flash("You Have Successfully Created A Category")
                except Exception as e:
                        flash(f"Error! Looks like there was a problem: {str(e)}")
            else: flash('A Category With This Name Already Exists')
    return render_template("category_manegment.html", categories = categories, form = form)

@app.route('/main/category_manegment/<name>', methods = ['GET','POST'])
@login_required
def specific_category(name):
    form = AddCategory()
    category_query = Categories.query.filter_by(name = name).first()
    
    if request.method == "POST" and form.validate_on_submit():
        category_to_update = Categories.query.filter_by(name = name).first()

        if category_to_update is not None:
            pic = form.category_img.data
            if pic:
                pic_filename = secure_filename(pic.filename)
                pic_name = str(uuid.uuid1()) + "_" + pic_filename
                pic.save(os.path.join(app.root_path, 'static', 'categories', pic_name))
            else:
                pic_name = None
            
            category_to_update.name = form.name.data
            category_to_update.category_img = pic_name
            try:
                db.session.commit()
                flash("You Updated Category Successfully")
            except Exception as e:
                flash(f"Error! Looks like there was a problem: {str(e)}")


    return render_template("specific_category.html", category = category_query, form = form)

@app.route('/items/<name>/delete',  methods=['GET','POST'] )
@login_required
def delete_category(name):

    category_to_delete = Categories.query.filter_by(name=name).first_or_404()

    if category_to_delete:
        items_ch = Items.query.filter_by(category = name).first()
        items_dep = Items_departure_temp.query.filter_by(category = name).first()
        if items_ch is None and items_dep is None:
            try:
                db.session.delete(category_to_delete)
                db.session.commit()
                flash("Category Was Deleted!")
                return redirect(url_for('category_manegment')) 

            except:
                flash("There Was Problem Deleting Category, Try Again.")
                return redirect(url_for('category_manegment')) 
        else: 
            flash("Items Are Attached To This Category, Deletion Is Impossible.")
            return redirect(url_for('specific_category', name = name)) 
    else: 
        flash("Category Was Not Found!")
        return redirect(url_for('category_manegment'))


@app.route('/user',  methods=['GET','POST'] )
def user():
    city = db.session.query(Warehouses.city).filter_by(warehouse_id=current_user.city_id).first()
    city = city[0]

    form = SignUpForm()
    form_password  = UpdatePassword()

    form.city.choices = [(warehouse.city, warehouse.city) for warehouse in Warehouses.query.all()]


    if request.method == "POST":
        user_to_update = Users.query.filter_by(id =current_user.id).first()
        if 'oldpassword' not in request.form:
            
            user = Users.query.filter_by(email = request.form['email']).first()

            city_res = db.session.query(Warehouses.warehouse_id).filter_by(city=request.form['city']).first()
            
            
            if (user_to_update is not None) and (user is None or user.id == current_user.id) :
                

                if check_password_hash(user_to_update.password, request.form['password']):
                    city_id_r = city_res[0]
                    
                    user_to_update.first_name = request.form['first_name']
                    user_to_update.last_name = request.form['last_name']
                    user_to_update.email = request.form['email']
                    user_to_update.city_id = city_id_r
                    try:
                            db.session.commit()
                            flash("You Updated User Successfully")

                    except Exception as e:
                            flash(f"Error! Looks like there was a problem: {str(e)}")
                    
                else: flash('Password Is Not Correct')
            else: flash('User Or City Was Not Found')
        else: 
            if check_password_hash(user_to_update.password, request.form['oldpassword']) and request.form['password'] == request.form['password2']:


                user_to_update.password = generate_password_hash(request.form['password'])
                try:
                        db.session.commit()
                        flash("You Updated Password Successfully")

                except Exception as e:
                        flash(f"Error! Looks like there was a problem: {str(e)}")
                    
            else: flash('Password Is Not Correct')

    return render_template("user.html", city = city, form  = form, form_password = form_password)

@app.route('/items/user/delete',  methods=['GET','POST'] )
@login_required
def delete_user():

    user_to_delete = Users.query.filter_by(id = current_user.id).first_or_404()

    if user_to_delete:
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("Profile Was Deleted!")
            return login()

        except:
            flash("There Was Problem Deleting User, Try Again.")
            return user()
    else: flash("User Was Not Found!")



@app.route('/sign_up', methods = ['GET','POST'])
def sign_up():
    form = SignUpForm()
    form.city.choices = [(warehouse.city, warehouse.city) for warehouse in Warehouses.query.all()]
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        city_check = select(Warehouses.warehouse_id).filter(Warehouses.city == form.city.data)
        city_result = db.session.execute(city_check).fetchone()

        if user is None and form.password.data==form.password2.data and city_result:

            city_id_r = city_result[0]

            user = Users(first_name = form.first_name.data, last_name = form.last_name.data, email = form.email.data,
                        city_id = city_id_r, password =generate_password_hash( form.password.data))
            db.session.add(user)
            db.session.commit()
            flash("You Signed Up Successfully")
        else:flash("Enter Correct Data")
        form.first_name.data = ''
        form.last_name.data = ''
        form.email.data = ''
        form.city.data = ''
        form.password.data = ''
        form.password2.data = ''
        

    return render_template('sign_up.html', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You Logged In Successfully")
                return redirect(url_for('main'))
            else:flash("Password Is Not Correct")
        else:flash("That User Does Not Exist")

    return render_template('login.html', form = form)

@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def log_out():
    logout_user()
    flash("You Have Been Logged Out")
    return redirect(url_for('index'))

@app.route('/main/suppliers', methods=['GET', 'POST'])
@login_required
def suppliers():
    form = AddSuppliers()
    suppliers_query = db.session.query(
        Suppliers.id,
        Suppliers.first_name,
        Suppliers.last_name,
        Suppliers.email,
        Suppliers.phone,
        Suppliers.city,
    )
    
    suppliers = suppliers_query.all()
    
    if request.method == "POST": 
        if form.validate_on_submit():
            email_check = request.form['email']
            phone_check = request.form['phone']
            existing_sup_email = Suppliers.query.filter_by(email=email_check).first()
            existing_sup_phone = Suppliers.query.filter_by(phone=phone_check).first()
            
            if existing_sup_email is None and existing_sup_phone is None:
                try:
                    supplier = Suppliers(
                        first_name=request.form['first_name'],
                        last_name=request.form['last_name'],
                        email=email_check,
                        phone=phone_check,
                        city=request.form['city']
                    )
                    db.session.add(supplier)
                    db.session.commit()
                    flash("You Have Successfully Added A Supplier")
                except Exception as e:
                    flash(f"Error! Looks like there was a problem: {str(e)}")
            else:
                flash('A Supplier With This Email or Phone Number Already Exists')
        else:
            sort_by = request.form.get('sort_by')
            order = request.form.get('order')
            if sort_by and order:
                suppliers_query = suppliers_query.order_by(getattr(getattr(Suppliers, sort_by), order)())  

    suppliers = suppliers_query.all()

    return render_template("suppliers.html", suppliers=suppliers, form=form)

@app.route('/main/suppliers/<int:id>', methods=['POST', 'GET'])
@login_required
def specific_supplier(id):
    supplier = db.session.query(
        Suppliers.id,
        Suppliers.first_name,
        Suppliers.last_name,
        Suppliers.email,
        Suppliers.phone,
        Suppliers.city,
        ).filter(
            Suppliers.id == id
        ).first_or_404()
    
    form = AddSuppliers()
    if request.method == "POST": 
        supplier_to_update = Suppliers.query.filter_by(id=id).first()
        if supplier_to_update is not None:
            email_check = request.form['email']
            phone_check = request.form['phone']
            
            existing_sup_email = Suppliers.query.filter(and_(Suppliers.email == email_check, Suppliers.id != id)).first()
            existing_sup_phone = Suppliers.query.filter(and_(Suppliers.phone == phone_check, Suppliers.id != id)).first()
            
            if existing_sup_email is None and existing_sup_phone is None:
                try:
                    supplier_to_update.first_name = request.form['first_name']
                    supplier_to_update.last_name = request.form['last_name']
                    supplier_to_update.email = email_check
                    supplier_to_update.phone = phone_check
                    supplier_to_update.city = request.form['city']
                    
                    db.session.commit()
                    flash("You Have Successfully Updated A Supplier")
                except Exception as e:
                    flash(f"Error! Looks like there was a problem: {str(e)}")
            else:
                flash('A Supplier With This Email or Phone Number Already Exists')
        else:
            flash("Supplier Was Not Found")

    return render_template("specific_supplier.html", supplier = supplier, form=form)

@app.route('/supplier/<int:id>/delete',  methods=['GET','POST'] )
@login_required
def delete_supplier(id):

    supplier_to_delete = Suppliers.query.filter_by(id=id).first_or_404()

    if supplier_to_delete:
        try:
            db.session.delete(supplier_to_delete)
            db.session.commit()
            flash("Supplier Was Deleted!")
            return suppliers()

        except:
            flash("There Was Problem Deleting Supplier, Try Again.")
            return suppliers()
    else: flash("Supplier Was Not Found!")

@app.route('/main/customers', methods=['GET', 'POST'])
@login_required
def customers():
    form = AddSuppliers()
    customers_query = db.session.query(
        Customers.id,
        Customers.first_name,
        Customers.last_name,
        Customers.email,
        Customers.phone,
        Customers.city,
    )
    
    
    if request.method == "POST": 
        if form.validate_on_submit():
            email_check = request.form['email']
            phone_check = request.form['phone']
            existing_cus_email = Customers.query.filter_by(email=email_check).first()
            existing_cus_phone = Customers.query.filter_by(phone=phone_check).first()
            
            if existing_cus_email is None and existing_cus_phone is None:
                try:
                    customer = Customers(
                        first_name=request.form['first_name'],
                        last_name=request.form['last_name'],
                        email=email_check,
                        phone=phone_check,
                        city=request.form['city']
                    )
                    db.session.add(customer)
                    db.session.commit()
                    flash("You Have Successfully Added A Customer")
                except Exception as e:
                    flash(f"Error! Looks like there was a problem: {str(e)}")
            else:
                flash('A Customer With This Email or Phone Number Already Exists')
        else:
            sort_by = request.form.get('sort_by')
            order = request.form.get('order')
            if sort_by and order:
                customers_query = customers_query.order_by(getattr(getattr(Customers, sort_by), order)())  

    customers = customers_query.all()

    return render_template("customers.html", customers=customers, form=form)

@app.route('/main/customers/<int:id>', methods=['POST', 'GET'])
@login_required
def specific_customer(id):
    customer = db.session.query(
        Customers.id,
        Customers.first_name,
        Customers.last_name,
        Customers.email,
        Customers.phone,
        Customers.city,
        ).filter(
            Customers.id == id
        ).first_or_404()
    
    form = AddSuppliers()
    if request.method == "POST": 
        customer_to_update = Customers.query.filter_by(id=id).first()
        if customer_to_update is not None:
            email_check = request.form['email']
            phone_check = request.form['phone']
            
            existing_cus_email = Customers.query.filter(and_(Customers.email == email_check, Customers.id != id)).first()
            existing_cus_phone = Customers.query.filter(and_(Customers.phone == phone_check, Customers.id != id)).first()
            
            if existing_cus_email is None and existing_cus_phone is None:
                try:
                    customer_to_update.first_name = request.form['first_name']
                    customer_to_update.last_name = request.form['last_name']
                    customer_to_update.email = email_check
                    customer_to_update.phone = phone_check
                    customer_to_update.city = request.form['city']
                    
                    db.session.commit()
                    flash("You Have Successfully Updated A Customer")
                except Exception as e:
                    flash(f"Error! Looks like there was a problem: {str(e)}")
            else:
                flash('A Customer With This Email or Phone Number Already Exists')
        else:
            flash("Customer Was Not Found")

    return render_template("specific_customer.html", customer = customer, form=form)

@app.route('/customer/<int:id>/delete',  methods=['GET','POST'] )
@login_required
def delete_customer(id):

    customer_to_delete = Customers.query.filter_by(id=id).first_or_404()

    if customer_to_delete:
        try:
            db.session.delete(customer_to_delete)
            db.session.commit()
            flash("Customer Was Deleted!")
            return customers()

        except:
            flash("There Was Problem Deleting Customer, Try Again.")
            return customers()
    else: flash("Customer Was Not Found!")


@app.route('/main/items/<type>', methods=['POST', 'GET'])
@login_required
def items(type):
    warehouse_alias = aliased(Warehouses)
    if type != 'all':
        items_query = db.session.query(
            Items.full_item_id,
            Items.item_model,
            Items.item_model_id,
            Items.category,
            Items.price,
            Items.producing_country,
            Items.colour,
            Items.manufacturer,
            Items.amount,
            Items.place,
            warehouse_alias.city.label('city')
        ).join(
            warehouse_alias
        ).filter(
            Items.city_id == warehouse_alias.warehouse_id,
            Items.category == type,
            Items.city_id == current_user.city_id
        )
    else:
        items_query = db.session.query(
            Items.full_item_id,
            Items.item_model,
            Items.item_model_id,
            Items.category,
            Items.price,
            Items.producing_country,
            Items.colour,
            Items.manufacturer,
            Items.amount,
            Items.place,
            warehouse_alias.city.label('city')
        ).join(
            warehouse_alias
        ).filter(
            Items.city_id == warehouse_alias.warehouse_id,
            Items.city_id == current_user.city_id
        )
    if request.method == "POST": 
        items_query = order(request, items_query)
    items = items_query.all()

    return render_template("items.html", items=items, type=type, route='items')

@app.route('/items/<int:full_item_id>',  methods=['GET','POST'])
@login_required
def specific_item(full_item_id):  
    item = db.session.query(
        Items.full_item_id,
        Items.item_model,
        Items.item_model_id,
        Items.category,
        Items.price,
        Items.producing_country,
        Items.colour,
        Items.manufacturer,
        Items.img,
        Items.bar_code,
        Items.place,
        Items.amount,
        select(Warehouses.city).where(Warehouses.warehouse_id == Items.city_id).label('city')
        ).filter(
            Items.full_item_id == full_item_id,
            Items.city_id == current_user.city_id
        ).first_or_404()
    
    form = Amount()
    form_d = Departure()
    form_d.city_to.choices = [(warehouse.city, warehouse.city) for warehouse in Warehouses.query.all()]
    if request.method == "POST":
        item_to_update = Items.query.filter_by(full_item_id=full_item_id, city_id=current_user.city_id).first()
        if 'city_to' not in request.form:
            if item_to_update is not None:
                if int(request.form['amount']) > 0:
                    item_to_update.amount = request.form['amount']
                    try:
                        new_action(full_item_id, 'Update amount')
                        db.session.commit()
                        flash("You Updated Item Successfully")
                    except Exception as e:
                        flash(f"Error! Looks like there was a problem: {str(e)}")
                else:flash("Amount must be a positive number")
            else: flash("Item Was Not Found")
        else:
            city_to = request.form['city_to']
            city = db.session.query(Warehouses.warehouse_id).filter(Warehouses.city == city_to).limit(1).scalar()

            if city and city!=current_user.city_id:
                if int(request.form['amountD']) > 0 :
                    if item_to_update.amount > int(request.form['amountD']):
                        
                        item_dep = Items_departure_temp(
                            full_item_id=full_item_id,
                            item_model=item_to_update.item_model,
                            item_model_id = item_to_update.item_model_id,
                            category= item_to_update.category,
                            city_from_id = current_user.city_id,
                            city_to_id= city,
                            price=item_to_update.price,
                            amount = int(request.form['amountD']),
                            place = "DEPARTURE",
                            producing_country= item_to_update.producing_country,
                            colour=item_to_update.colour,
                            manufacturer=item_to_update.manufacturer,
                            img=item_to_update.img,
                            bar_code=item_to_update.bar_code
                        )
                        db.session.add(item_dep)
                        new_action(full_item_id, f'Departute item to {request.form['city_to']}. Amount {int(request.form['amountD'])}')

                        item_to_update.amount = item_to_update.amount -  int(request.form['amountD'])
                        new_action(full_item_id, 'Update amount')

                        db.session.commit()
                        flash("You Have Successfully Created A Departure")
                            
                    elif item_to_update.amount == int(request.form['amountD']):
                        item_dep = Items_departure_temp(
                            full_item_id=full_item_id,
                            item_model=item_to_update.item_model,
                            item_model_id = item_to_update.item_model_id,
                            category= item_to_update.category,
                            city_from_id = current_user.city_id,
                            city_to_id= city,
                            price=item_to_update.price,
                            amount = int(request.form['amountD']),
                            place = "DEPARTURE",
                            producing_country= item_to_update.producing_country,
                            colour=item_to_update.colour,
                            manufacturer=item_to_update.manufacturer,
                            img=item_to_update.img,
                            bar_code=item_to_update.bar_code
                        )
                        db.session.add(item_dep)
                        new_action(full_item_id, f'Departute item to {request.form['city_to']}. Amount {int(request.form['amountD'])}')

                        db.session.delete(item_to_update)
                        new_action(full_item_id, 'Delete}')

                        db.session.commit()
                        flash("You Have Successfully Created A Departure")

                    else: flash("There Are Not So Many Of This Product")
                else: flash("Amount must be a positive number")
            else:flash("Error! No such city was found or item is in this location")

    return render_template("specific_item.html", item=item, form=form, form_d=form_d)


@app.route('/items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = AddItemForm()
    form.category.choices = [(category.name, category.name) for category in Categories.query.all()]
    is_empty = Categories.query.first() 
    if is_empty is None:
        flash('Create categories first')
    else:
        if form.validate_on_submit():
            ean_digits = form.producing_country_id.data + form.manufacturer_id.data + form.item_model_id.data 
            odd_sum = sum(int(ean_digits[i]) for i in range(0, 12))
            even_sum = sum(int(ean_digits[i]) for i in range(1, 11, 2)) * 3
            checksum = (10 - ((odd_sum + even_sum) % 10)) % 10
            ean_digits = ean_digits + str(checksum)
            
            item = Items.query.filter_by(full_item_id=ean_digits, city_id = current_user.city_id).first()
            
            if item is None:

                item = Items.query.filter_by(full_item_id=ean_digits).first()

                if item is None:
                
                    if len(form.producing_country_id.data) == 3 or len(form.manufacturer_id.data) == 4 or len(form.item_model_id.data):
                        pic = request.files['img']
                        if pic:
                            pic_filename = secure_filename(pic.filename)
                            pic_name = str(uuid.uuid1()) + "_" + pic_filename
                            pic.save(os.path.join(app.root_path, 'static', 'img', pic_name))
                        else:
                            pic_name = None

    
                        ean = barcode.get_barcode_class('ean13')

                        barcode_instance = ean(ean_digits, writer=ImageWriter())
                        barcode_filename = 'barcode_' + ean_digits  
                        barcode_path = os.path.join(app.root_path, 'static', 'barcode', barcode_filename)

                        barcode_instance.save(barcode_path)

                        
                        
                        item = Items(
                            full_item_id=int(ean_digits),
                            item_model=form.item_model.data,
                            item_model_id = form.item_model_id.data,
                            category=form.category.data,
                            city_id=current_user.city_id,
                            price=form.price.data,
                            amount = form.amount.data,
                            place = form.place.data,
                            producing_country=form.producing_country.data,
                            colour=form.colour.data,
                            manufacturer=form.manufacturer.data,
                            img=pic_name,
                            bar_code= barcode_filename + '.png'
                        )
                        db.session.add(item)
                        new_action(int(ean_digits), 'Added item')
                        db.session.commit()
                        flash("You Added Item Successfully")
                        return items('all')
                        
                    else: flash("Enter Correct Data")
                else: 
                    form_check = select(Items.item_model, Items.category, Items.price ,Items.producing_country, Items.colour, Items.manufacturer,
                                        Items.img, Items.bar_code).filter(Items.full_item_id == ean_digits).limit(1)
                    form_check_result = db.session.execute(form_check).fetchone()

                    if form.item_model.data == form_check_result[0] and form.category.data == form_check_result[1] and form.price.data == form_check_result[2] and form.producing_country.data == form_check_result[3] and form.colour.data == form_check_result[4] and form.manufacturer.data == form_check_result[5]:
                        item = Items(
                            full_item_id=int(ean_digits),
                            item_model=form.item_model.data,
                            item_model_id = form.item_model_id.data,
                            category=form.category.data,
                            city_id=current_user.city_id,
                            price=form.price.data,
                            amount = form.amount.data,
                            place = form.place.data,
                            producing_country=form.producing_country.data,
                            colour=form.colour.data,
                            manufacturer=form.manufacturer.data,
                            img=form_check_result[6],
                            bar_code=form_check_result[7]
                        )
                        db.session.add(item)
                        new_action(int(ean_digits), 'Added item')
                        db.session.commit()
                        flash("You Added Item Successfully")
                        return items('all')
                    
                    else:flash("One Of The Entered Item values For This id, Which Is Located In Another City, Does Not Match The Existing Ones")
            else:
                flash("An Item With This Full Item ID and City Already Exists")
                
            form_clean(form)
        
    return render_template('add_item.html', form=form)

@app.route('/items/<int:full_item_id>/delete',  methods=['GET','POST'] )
@login_required
def delete_item(full_item_id):

    item_to_delete = Items.query.filter_by(full_item_id=full_item_id, city_id=current_user.city_id).first_or_404()

    if item_to_delete:
        try:
            db.session.delete(item_to_delete)
            db.session.commit()
            flash("Item Was Deleted!")
            return items('all')

        except:
            flash("There Was Problem Deleting Item, Try Again.")
            return items('all')
    else: flash("Item Was Not Found!")
       
@app.route('/items/<int:full_item_id>/update',  methods=['GET','POST'] )
@login_required
def update_item(full_item_id):
    form = AddItemForm()
    form.category.choices = [(category.name, category.name) for category in Categories.query.all()]
    if form.validate_on_submit():
        def calculate_checksum(ean_digits):
            odd_sum = sum(int(ean_digits[i]) for i in range(0, 12))
            even_sum = sum(int(ean_digits[i]) for i in range(1, 11, 2)) * 3
            checksum = (10 - ((odd_sum + even_sum) % 10)) % 10
            return str(checksum)
        
        ean_digits = form.producing_country_id.data + form.manufacturer_id.data + form.item_model_id.data 
        checksum = calculate_checksum(ean_digits)
        ean_digits = ean_digits + checksum
        
        
        item_to_update = Items.query.filter_by(full_item_id=full_item_id, city_id = current_user.city_id).first()
        if item_to_update is not None:

            item_exist = Items.query.filter(Items.full_item_id == ean_digits, not_(Items.city_id == current_user.city_id)).first()

            if item_exist is None :
            
                if  len(form.producing_country_id.data) == 3 or len(form.manufacturer_id.data) == 4 or len(form.item_model_id.data):
                    pic = request.files['img']
                    if pic:
                        pic_filename = secure_filename(pic.filename)
                        pic_name = str(uuid.uuid1()) + "_" + pic_filename
                        pic.save(os.path.join(app.root_path, 'static', 'img', pic_name))
                    else:
                        pic_name = None

                    ean = barcode.get_barcode_class('ean13')
                    barcode_instance = ean(ean_digits, writer=ImageWriter())
                    barcode_filename = 'barcode_' + ean_digits
                    barcode_path = os.path.join(app.root_path, 'static', 'barcode', barcode_filename)
                    barcode_instance.save(barcode_path)
                    
                    
                    item_to_update.full_item_id=int(ean_digits),
                    item_to_update.item_model=form.item_model.data,
                    item_to_update.item_model_id = form.item_model_id.data,
                    item_to_update.category=form.category.data,
                    item_to_update.city_id=current_user.city_id,
                    item_to_update.price=form.price.data,
                    item_to_update.amount = form.amount.data,
                    item_to_update.place = form.place.data,
                    item_to_update.producing_country=form.producing_country.data,
                    item_to_update.colour=form.colour.data,
                    item_to_update.manufacturer=form.manufacturer.data,
                    item_to_update.img=pic_name,
                    item_to_update.bar_code=barcode_filename + '.png'
                    try:
                        new_action(int(ean_digits), 'Updated item')
                        db.session.commit()
                        flash("You Updated Item Successfully")
                        return specific_item(ean_digits)
                    except: 
                        flash("Error!  Looks like there was a problem...try again!")
                        return specific_item(full_item_id)
                    
                else: flash("Enter Correct Data")
            else: 
                form_check = select(Items.item_model, Items.category, Items.price ,Items.producing_country, Items.colour, Items.manufacturer,
                                    Items.img, Items.bar_code).filter(Items.full_item_id == ean_digits).limit(1)
                form_check_result = db.session.execute(form_check).fetchone()

                if form.item_model.data == form_check_result[0] and form.category.data == form_check_result[1] and form.price.data == form_check_result[2] and form.producing_country.data == form_check_result[3] and form.colour.data == form_check_result[4] and form.manufacturer.data == form_check_result[5]:
                    item_to_update.full_item_id=int(ean_digits),
                    item_to_update.item_model=form.item_model.data,
                    item_to_update.item_model_id = form.item_model_id.data,
                    item_to_update.category=form.category.data,
                    item_to_update.city_id=current_user.city_id,
                    item_to_update.price=form.price.data,
                    item_to_update.amount = form.amount.data,
                    item_to_update.place = form.place.data,
                    item_to_update.producing_country=form.producing_country.data,
                    item_to_update.colour=form.colour.data,
                    item_to_update.manufacturer=form.manufacturer.data,
                    item_to_update.img=pic_name,
                    item_to_update.bar_code=barcode_filename + '.png'
                    try:
                        new_action(int(ean_digits), 'Updated item')
                        db.session.commit()
                        flash("You Updated Item Successfully")
                        return specific_item(ean_digits)
                    except: 
                        flash("Error!  Looks like there was a problem...try again!")
                        return specific_item(full_item_id)
                else:flash("One Of The Entered Item values For This id, Which Is Located In Another City, Does Not Match The Existing Ones")
        else:
            flash("An Item With This Full Item ID and City Not Exists")
            
        form_clean(form)
        
    return render_template('update_item.html', form=form, full_item_id=full_item_id)


@app.route('/items/<int:full_item_id>/history',  methods=['GET','POST'] )
@login_required
def history(full_item_id):
    items = db.session.query(
        Items_actions.action_id,
        Items_actions.full_item_id,
        Items_actions.action,
        Items_actions.date_action,
        select(Warehouses.city).where(Warehouses.warehouse_id == Items_actions.city_id).label('city'),
        select(Users.first_name).where(Users.id == Items_actions.user_id).label('first_name_user'),
        select(Users.last_name).where(Users.id == Items_actions.user_id).label('last_name_user'),
        ).filter(
            Items.full_item_id == full_item_id,
            Items.city_id == current_user.city_id
        ).all()
    return render_template('history.html', items=items, full_item_id = full_item_id)



        
@app.context_processor
def for_search():
    form = SearchForm()
    return dict(form=form)


@app.route('/main/search', methods=['POST', 'GET'])
@login_required
def search():
    global items_query
    global type

    form = SearchForm()
    items = Items.query
    if form.validate_on_submit():
        
        search_query = form.searched.data
        type = form.searched.data
        warehouse_alias = aliased(Warehouses)
        items_query = db.session.query(
            Items.full_item_id,
            Items.item_model,
            Items.item_model_id,
            Items.category,
            Items.price,
            Items.producing_country,
            Items.colour,
            Items.manufacturer,
            Items.amount,
            Items.place,
            warehouse_alias.city.label('city')
        ).join(
            warehouse_alias
        ).filter(
            Items.city_id == warehouse_alias.warehouse_id,
            Items.city_id == current_user.city_id,
            (Items.item_model.like(f"%{search_query}%")) |
            (Items.item_model_id.like(f"%{search_query}%")) |
            (Items.full_item_id.like(f"%{search_query}%"))
        )
        items = items_query.all()
        return render_template("items.html", items=items, route='search_order', type = type)
    
    return render_template("items.html", items=items, route='search_order', type = type)

@app.route('/main/search_order/<type>',  methods=['GET','POST'] )
@login_required
def search_order(type):


    items_query_local = items_query
    items_query_local = order(request, items_query_local)
    items = items_query_local.all()
    

    return render_template("items.html", items=items, type=type, route='search_order')

@app.route('/main/departure',  methods=['GET','POST'] )
@login_required
def departure():
    form = AcceptTheDeparture()
    city = db.session.query(Warehouses.city).filter(Warehouses.warehouse_id == current_user.city_id).limit(1).scalar()
    items = None
    warehouse_alias = aliased(Warehouses)

    items_query = db.session.query(
        Items_departure_temp.departure_id,
        Items_departure_temp.full_item_id,
        Items_departure_temp.item_model,
        Items_departure_temp.item_model_id,
        Items_departure_temp.category,
        Items_departure_temp.price,
        Items_departure_temp.producing_country,
        Items_departure_temp.colour,
        Items_departure_temp.manufacturer,
        Items_departure_temp.amount,
        Items_departure_temp.place,
        warehouse_alias.city.label('city_from')
    ).join(
        warehouse_alias,
        Items_departure_temp.city_from_id == warehouse_alias.warehouse_id
    ).filter(
        Items_departure_temp.city_from_id == warehouse_alias.warehouse_id,
        Items_departure_temp.city_to_id == current_user.city_id
    )
    items = items_query.all()

    if request.method == "POST": 
        full_item_id = request.args.get('full_item_id')
        if not full_item_id:
            flash('Error! Something Went Wrong, Please Try Again.')
        else:
            item_to_update = Items.query.filter_by(full_item_id=full_item_id, city_id=current_user.city_id).first()
            item_dep = Items_departure_temp.query.filter_by(full_item_id=full_item_id, city_to_id=current_user.city_id ).first()
            if not item_to_update:
                try:
                    item = Items(
                        full_item_id=full_item_id,
                        item_model=item_dep.item_model,
                        item_model_id = item_dep.item_model_id,
                        category=item_dep.category,
                        city_id=current_user.city_id,
                        price=item_dep.price,
                        amount = item_dep.amount,
                        place = form.place.data,
                        producing_country=item_dep.producing_country,
                        colour=item_dep.colour,
                        manufacturer=item_dep.manufacturer,
                        img=item_dep.img,
                        bar_code=item_dep.bar_code
                    )
                    db.session.add(item)
                    db.session.delete(item_dep)

                    db.session.commit()

                    flash("You Accepted Departure Successfully")
                    new_action(full_item_id, 'Accepted Departure')
                    
                except Exception as e:
                    flash(f"Error! Looks like there was a problem: {str(e)}")
            else: 
                if form.place.data != item_to_update.place:
                    flash(f"The Entered Storage Location For The Item In The Warehouse Does Not Match The Existing One: {item_to_update.place}")
                else:
                    item_to_update.amount = item_to_update.amount + item_dep.amount
                    try:    
                        new_action(full_item_id, 'Accepted Departure')
                        db.session.commit()
                        flash("You Accepted Departure Successfully")
                    except Exception as e:
                        flash(f"Error! Looks like there was a problem: {str(e)}")


    return render_template("departure.html", city = city, items = items, form = form)





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)