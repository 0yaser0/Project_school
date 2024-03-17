from flask import Blueprint, render_template, request,redirect, url_for
from datetime import datetime
from DB import mysql

bp = Blueprint('routes', __name__)

products = {}
Sales_Product = {}

def calculate_Totals_Sales():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.date, p.prodPrice, s.quantity
        FROM products_db.sales s
        INNER JOIN products_db.product p ON p.id = s.product_id
    """)
    sales_data = cur.fetchall()
    Totals_Sales = {}
    for date, price, quantity in sales_data:
        if date not in Totals_Sales:
            Totals_Sales[date] = 0
        Totals_Sales[date] += price * quantity
    cur.close()
    return Totals_Sales


@bp.route('/')
def HomePage():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product")
    mysql.connection.commit()
    fetchdata = cur.fetchall()
    cur.close()
    return render_template('HomePage.html', data=fetchdata)

@bp.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        prodName = request.form.get('name')
        prodDesc = request.form.get('description')
        prodPrice = request.form.get('price')
        prodInStock = request.form.get('quantity')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO product (prodName, prodDesc, prodPrice, prodInStock) VALUES (%s, %s, %s, %s)", (prodName, prodDesc, prodPrice, prodInStock))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('routes.HomePage'))
    return render_template('HomePage.html', products=products.values(), Totals_Sales=Totals_Sales)

@bp.route('/Update_Product/<int:id>', methods=['GET', 'POST'])
def Update_Product(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        prodName = request.form.get('name')
        prodDesc = request.form.get('description')
        prodPrice = request.form.get('price')
        prodInStock = request.form.get('quantity')
        cur.execute("UPDATE product SET prodName=%s, prodDesc=%s, prodPrice=%s, prodInStock=%s WHERE id=%s", (prodName, prodDesc, prodPrice, prodInStock, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('routes.HomePage')) 
    cur.execute("SELECT * FROM product WHERE id=%s", [id])
    product = cur.fetchone()
    return render_template('Update_Product.html', product=product)


@bp.route('/delete/<int:id>')
def delete_product(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM sales WHERE product_id=%s", [id])
    cur.execute("DELETE FROM product WHERE id=%s", [id])
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('routes.HomePage'))



@bp.route('/sale', methods=['POST'])
def add_sale():
    product_id = int(request.form.get('product_id')) 
    quantity = int(request.form.get('quantity'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT prodInStock FROM product WHERE id=%s", [product_id])
    product_in_stock = cur.fetchone()
    if product_in_stock is not None and product_in_stock[0] >= quantity:
        cur.execute("UPDATE product SET prodInStock=%s WHERE id=%s", (product_in_stock[0] - quantity, product_id))
        cur.execute("INSERT INTO sales (product_id, quantity, date) VALUES (%s, %s, %s)", (product_id, quantity, datetime.now().date()))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('routes.HomePage'))
    else:
        cur.close()
        return redirect(url_for('routes.HomePage', message='Not enough stock'))


@bp.route('/Totals_Sales')
def Totals_Sales():
    Totals_Sales = calculate_Totals_Sales()
    return render_template('Totals_Sales.html', Totals_Sales=Totals_Sales.items())

@bp.route('/Sales_Product')
def view_Sales_Product():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM sales")
    sales_data = cur.fetchall()
    cur.close()
    return render_template('Sales_Product.html', Sales_Product=sales_data)
