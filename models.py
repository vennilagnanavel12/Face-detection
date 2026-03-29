from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # hospital, clinic, medical_shop
    organization_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    license_number = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    @property
    def is_active(self):
        return self.active
    
    # Relationships
    patients = db.relationship('Patient', backref='created_by_user', lazy=True)
    prescriptions = db.relationship('Prescription', backref='prescribed_by', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(6), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.Text, nullable=False)
    emergency_contact = db.Column(db.String(15), nullable=False)
    blood_group = db.Column(db.String(5))
    allergies = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    diseases = db.relationship('Disease', backref='patient', lazy=True, cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def generate_patient_id(self):
        """Generate a unique 6-character patient ID"""
        while True:
            patient_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Patient.query.filter_by(patient_id=patient_id).first():
                return patient_id
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        today = datetime.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    def __repr__(self):
        return f'<Patient {self.patient_id}: {self.full_name}>'

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    diagnosis_date = db.Column(db.Date, nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # mild, moderate, severe
    status = db.Column(db.String(20), nullable=False, default='active')  # active, recovered, chronic
    notes = db.Column(db.Text)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    diagnosed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Disease {self.name} for Patient {self.patient_id}>'

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prescription_number = db.Column(db.String(10), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    prescribed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, fulfilled, expired
    
    # Relationships
    medicines = db.relationship('PrescriptionMedicine', backref='prescription', lazy=True, cascade='all, delete-orphan')
    
    def generate_prescription_number(self):
        """Generate a unique prescription number"""
        while True:
            prescription_number = 'RX' + ''.join(random.choices(string.digits, k=8))
            if not Prescription.query.filter_by(prescription_number=prescription_number).first():
                return prescription_number
    
    def __repr__(self):
        return f'<Prescription {self.prescription_number}>'

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    generic_name = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    category = db.Column(db.String(50), nullable=False)
    strength = db.Column(db.String(50))
    form = db.Column(db.String(30), nullable=False)  # tablet, capsule, syrup, injection
    price_per_unit = db.Column(db.Numeric(10, 2))
    description = db.Column(db.Text)
    side_effects = db.Column(db.Text)
    contraindications = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    prescriptions = db.relationship('PrescriptionMedicine', backref='medicine', lazy=True)
    inventory = db.relationship('MedicineInventory', backref='medicine', lazy=True)
    
    def __repr__(self):
        return f'<Medicine {self.name}>'

class PrescriptionMedicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)  # once daily, twice daily, etc.
    duration = db.Column(db.String(50), nullable=False)  # 7 days, 1 month, etc.
    timing = db.Column(db.String(50))  # before food, after food, with food
    special_instructions = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PrescriptionMedicine ID:{self.id} - {self.dosage}>'

class MedicineInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    medical_shop_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    batch_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    cost_price = db.Column(db.Numeric(10, 2))
    selling_price = db.Column(db.Numeric(10, 2))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    medical_shop = db.relationship('User', backref='inventory', lazy=True)
    
    def __repr__(self):
        return f'<Inventory ID:{self.id}: {self.stock_quantity}>'

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_number = db.Column(db.String(10), unique=True, nullable=False)
    medical_shop_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.id'))
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(10, 2), default=0)
    final_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, card, upi
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    medical_shop = db.relationship('User', backref='sales', lazy=True)
    patient = db.relationship('Patient', backref='purchases', lazy=True)
    prescription = db.relationship('Prescription', backref='sales', lazy=True)
    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')
    
    def generate_sale_number(self):
        """Generate a unique sale number"""
        while True:
            sale_number = 'SL' + ''.join(random.choices(string.digits, k=8))
            if not Sale.query.filter_by(sale_number=sale_number).first():
                return sale_number
    
    def __repr__(self):
        return f'<Sale {self.sale_number}>'

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationships
    medicine = db.relationship('Medicine', backref='sale_items', lazy=True)
    
    def __repr__(self):
        return f'<SaleItem {self.medicine.name}: {self.quantity}>'
