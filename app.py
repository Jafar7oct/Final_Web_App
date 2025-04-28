from flask import Flask, render_template, url_for, abort, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import json
from datetime import timedelta
import secrets
from markupsafe import escape

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

app = Flask(__name__)
app.config['DEBUG'] = False  # Disable debug mode in production
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))  # Secure random key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://user:password@db:3306/orbitronic')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS-only cookies
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JS access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session timeout

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.String(50), primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    details = db.Column(db.JSON, nullable=True)

# Input validation helper
def validate_input(field, max_length, field_name):
    if not field:
        return f"{field_name} is required"
    if len(field) > max_length:
        return f"{field_name} is too long"
    return None

# Initialize database and seed data
def init_db():
    app.logger.info("Initializing database...")
    try:
        db.create_all()
        app.logger.info("Tables created successfully")
        
        if not User.query.first():
            app.logger.info("Seeding initial users...")
            admin = User(
                username='admin',
                password=generate_password_hash('admin123', method='pbkdf2:sha256', salt_length=16),
                role='admin'
            )
            user = User(
                username='user',
                password=generate_password_hash('user123', method='pbkdf2:sha256', salt_length=16),
                role='user'
            )
            db.session.add_all([admin, user])
            db.session.commit()
            app.logger.info("Users seeded successfully")
        
        if not Product.query.first():
            app.logger.info("Seeding initial products...")
            initial_products = {
                'phones': [
                    {
                        'id': 'iphone-15-pro',
                        'name': 'iPhone 15 Pro',
                        'price': 999,
                        'description': 'Latest Apple flagship phone',
                        'image': 'iphone15pro.jpg',
                        'details': {
                            'screen': '6.1-inch Super Retina XDR display',
                            'chip': 'A17 Pro chip',
                            'camera': '48MP Main | 12MP Ultra Wide | 12MP Telephoto',
                            'battery': 'Up to 23 hours video playback',
                            'colors': ['Natural Titanium', 'Blue Titanium', 'White Titanium', 'Black Titanium']
                        }
                    },
                    {
                        'id': 'samsung-s24',
                        'name': 'Samsung Galaxy S24',
                        'price': 899,
                        'description': 'Premium Android smartphone',
                        'image': 's24.jpg',
                        'details': {
                            'screen': '6.2-inch Dynamic AMOLED 2X',
                            'chip': 'Snapdragon 8 Gen 3',
                            'camera': '50MP Main | 12MP Ultra Wide | 10MP Telephoto',
                            'battery': '4,000 mAh',
                            'colors': ['Phantom Black', 'Cream', 'Violet', 'Mint']
                        }
                    }
                ],
                'laptops': [
                    {
                        'id': 'macbook-pro',
                        'name': 'MacBook Pro',
                        'price': 1299,
                        'description': 'Powerful laptop for professionals',
                        'image': 'macbook.jpg',
                        'details': {
                            'screen': '14-inch Liquid Retina XDR display',
                            'chip': 'M3 Pro chip',
                            'memory': 'Up to 36GB unified memory',
                            'storage': 'Up to 4TB SSD',
                            'battery': 'Up to 18 hours'
                        }
                    },
                    {
                        'id': 'dell-xps',
                        'name': 'Dell XPS 15',
                        'price': 1199,
                        'description': 'Premium Windows laptop',
                        'image': 'xps15.jpg',
                        'details': {
                            'screen': '15.6-inch 4K OLED touch display',
                            'processor': '13th Gen Intel Core i9',
                            'memory': 'Up to 64GB DDR5',
                            'storage': 'Up to 4TB SSD',
                            'battery': 'Up to 12 hours'
                        }
                    }
                ]
            }
            for category, items in initial_products.items():
                for item in items:
                    product = Product(
                        id=item['id'],
                        category=category,
                        name=item['name'],
                        price=item['price'],
                        description=item['description'],
                        image=item['image'],
                        details=json.dumps(item['details'])
                    )
                    db.session.add(product)
            db.session.commit()
            app.logger.info("Products seeded successfully")
    except Exception as e:
        app.logger.error(f"Error initializing database: {str(e)}")
        db.session.rollback()
        raise

# Initialize database
with app.app_context():
    app.logger.info("Calling init_db...")
    init_db()

# Routes
@app.route('/')
def home():
    try:
        app.logger.info("Rendering home page")
        products = {
            'phones': Product.query.filter_by(category='phones').all(),
            'laptops': Product.query.filter_by(category='laptops').all()
        }
        for category in products:
            for product in products[category]:
                product.details = json.loads(product.details) if product.details else {}
        return render_template('index.html', products=products)
    except Exception as e:
        app.logger.error(f"Error in home route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/about')
def about():
    try:
        app.logger.info("Rendering about page")
        return render_template('about.html')
    except Exception as e:
        app.logger.error(f"Error in about route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/contact')
def contact():
    try:
        app.logger.info("Rendering contact page")
        return render_template('contact.html')
    except Exception as e:
        app.logger.error(f"Error in contact route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = escape(request.form.get('username', ''))
            password = request.form.get('password', '')
            
            username_error = validate_input(username, 50, "Username")
            if username_error:
                flash(username_error, 'error')
                return render_template('login.html')
                
            if not password:
                flash('Password is required', 'error')
                return render_template('login.html')

            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['username'] = user.username
                session['role'] = user.role
                session.permanent = True
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'error')
        return render_template('login.html')
    except Exception as e:
        app.logger.error(f"Error in login route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'POST':
            username = escape(request.form.get('username', ''))
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            username_error = validate_input(username, 50, "Username")
            password_error = validate_input(password, 255, "Password")
            if username_error:
                flash(username_error, 'error')
                return render_template('signup.html')
            if password_error:
                flash(password_error, 'error')
                return render_template('signup.html')
            if len(password) < 8:
                flash('Password must be at least 8 characters long', 'error')
                return render_template('signup.html')

            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
            elif password != confirm_password:
                flash('Passwords do not match', 'error')
            else:
                new_user = User(
                    username=username,
                    password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=16),
                    role='user'
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Signup successful! Please login.', 'success')
                return redirect(url_for('login'))
        return render_template('signup.html')
    except Exception as e:
        app.logger.error(f"Error in signup route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/admin')
def admin():
    try:
        if 'username' not in session or session.get('role') != 'admin':
            flash('You must be an admin to access this page', 'error')
            return redirect(url_for('login'))
        app.logger.info("Rendering admin page")
        products = {
            'phones': Product.query.filter_by(category='phones').all(),
            'laptops': Product.query.filter_by(category='laptops').all()
        }
        return render_template('admin.html', products=products)
    except Exception as e:
        app.logger.error(f"Error in admin route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/add_product', methods=['POST'])
def add_product():
    try:
        if 'username' not in session or session.get('role') != 'admin':
            flash('You must be an admin to perform this action', 'error')
            return redirect(url_for('login'))
        
        category = escape(request.form.get('category', ''))
        product_id = escape(request.form.get('id', ''))
        name = escape(request.form.get('name', ''))
        price = request.form.get('price', '')
        description = escape(request.form.get('description', ''))
        image = escape(request.form.get('image', ''))
        details = request.form.get('details', '')

        validations = [
            validate_input(category, 50, "Category"),
            validate_input(product_id, 50, "Product ID"),
            validate_input(name, 100, "Name"),
            validate_input(description, 1000, "Description"),
            validate_input(image, 100, "Image")
        ]
        for error in validations:
            if error:
                flash(error, 'error')
                return redirect(url_for('admin'))

        try:
            price = int(price)
            if price <= 0:
                flash('Price must be positive', 'error')
                return redirect(url_for('admin'))
        except ValueError:
            flash('Invalid price format', 'error')
            return redirect(url_for('admin'))

        if Product.query.filter_by(id=product_id).first():
            flash('Product ID already exists', 'error')
            return redirect(url_for('admin'))

        try:
            details_json = json.loads(details) if details else {}
        except json.JSONDecodeError:
            flash('Invalid JSON format for details', 'error')
            return redirect(url_for('admin'))

        new_product = Product(
            id=product_id,
            category=category,
            name=name,
            price=price,
            description=description,
            image=image,
            details=json.dumps(details_json)
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully', 'success')
        return redirect(url_for('admin'))
    except Exception as e:
        app.logger.error(f"Error in add_product route: {str(e)}")
        flash('An error occurred while adding the product', 'error')
        return redirect(url_for('admin'))

@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    try:
        if 'username' not in session or session.get('role') != 'admin':
            flash('You must be an admin to perform this action', 'error')
            return redirect(url_for('login'))

        product = Product.query.filter_by(id=product_id).first()
        if not product:
            abort(404)

        if request.method == 'POST':
            category = escape(request.form.get('category', ''))
            name = escape(request.form.get('name', ''))
            price = request.form.get('price', '')
            description = escape(request.form.get('description', ''))
            image = escape(request.form.get('image', ''))
            details = request.form.get('details', '')

            validations = [
                validate_input(category, 50, "Category"),
                validate_input(name, 100, "Name"),
                validate_input(description, 1000, "Description"),
                validate_input(image, 100, "Image")
            ]
            for error in validations:
                if error:
                    flash(error, 'error')
                    return redirect(url_for('edit_product', product_id=product_id))

            try:
                price = int(price)
                if price <= 0:
                    flash('Price must be positive', 'error')
                    return redirect(url_for('edit_product', product_id=product_id))
            except ValueError:
                flash('Invalid price format', 'error')
                return redirect(url_for('edit_product', product_id=product_id))

            try:
                details_json = json.loads(details) if details else {}
            except json.JSONDecodeError:
                flash('Invalid JSON format for details', 'error')
                return redirect(url_for('edit_product', product_id=product_id))

            product.category = category
            product.name = name
            product.price = price
            product.description = description
            product.image = image
            product.details = json.dumps(details_json)
            db.session.commit()
            flash('Product updated successfully', 'success')
            return redirect(url_for('admin'))

        product.details = json.loads(product.details) if product.details else {}
        return render_template('edit_product.html', product=product)
    except Exception as e:
        app.logger.error(f"Error in edit_product route: {str(e)}")
        flash('An error occurred while editing the product', 'error')
        return redirect(url_for('admin'))

@app.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        if 'username' not in session or session.get('role') != 'admin':
            flash('You must be an admin to perform this action', 'error')
            return redirect(url_for('login'))

        product = Product.query.filter_by(id=product_id).first()
        if not product:
            abort(404)
        
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully', 'success')
        return redirect(url_for('admin'))
    except Exception as e:
        app.logger.error(f"Error in delete_product route: {str(e)}")
        flash('An error occurred while deleting the product', 'error')
        return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    try:
        session.pop('username', None)
        session.pop('role', None)
        flash('Logged out successfully', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        app.logger.error(f"Error in logout route: {str(e)}")
        return render_template('500.html'), 500

@app.route('/product/<product_id>')
def product_detail(product_id):
    try:
        app.logger.info(f"Fetching product details for {product_id}")
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            app.logger.warning(f"Product not found: {product_id}")
            abort(404)
        product.details = json.loads(product.details) if product.details else {}
        return render_template('product_detail.html', product=product)
    except Exception as e:
        app.logger.error(f"Error in product_detail route: {str(e)}")
        return render_template('500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
