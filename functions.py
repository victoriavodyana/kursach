from main import current_user
from models import Items_actions, Items
from datetime import datetime, timezone
from config import app, db
from flask import request, jsonify, render_template,Flask,flash


def form_clean(form):
    form.item_model.data = ''
    form.item_model_id.data = ''
    form.category.data = ''
    form.price.data = 0
    form.producing_country.data = ''
    form.producing_country_id.data = ''
    form.colour.data = ''
    form.manufacturer.data = ''
    form.manufacturer_id.data = ''
    form.amount.data = 0
    form.place.data = ''
    form.img.data = None

def new_action(full_item_id, action):
    new_action = Items_actions(
            full_item_id=full_item_id,
            user_id=current_user.id,
            city_id = current_user.city_id,
            action=action,
            date_action=datetime.now(timezone.utc)
            )
    db.session.add(new_action)

def order(request,items_query):
    sort_by = request.form.get('sort_by')
    order = request.form.get('order')
    if sort_by and order:
        items_query = items_query.order_by(getattr(getattr(Items, sort_by), order)())
    return items_query




