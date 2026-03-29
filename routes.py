from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import app, db
from models import User, Patient, Disease, Medicine, Prescription, PrescriptionMedicine, MedicineInventory, Sale, SaleItem
from forms import (LoginForm, RegistrationForm, PatientRegistrationForm, PatientSearchForm, 
                   DiseaseForm, MedicineForm, PrescriptionForm, PrescriptionMedicineForm, InventoryForm)
from utils import (generate_unique_patient_id, generate_unique_prescription_number, 
                   get_role_color, calculate_age, format_currency)
from datetime import datetime, date, timedelta
from sqlalchemy import or_, desc

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.active:
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('auth/register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('auth/register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            organization_name=form.organization_name.data,
            phone=form.phone.data,
            address=form.address.data,
            license_number=form.license_number.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            app.logger.error(f"Registration error: {e}")
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get dashboard statistics
    total_patients = Patient.query.filter_by(created_by=current_user.id).count()
    
    if current_user.role == 'hospital':
        recent_patients = Patient.query.filter_by(created_by=current_user.id).order_by(desc(Patient.created_at)).limit(5).all()
        total_prescriptions = Prescription.query.filter_by(prescribed_by_id=current_user.id).count()
        return render_template('dashboard/hospital.html', 
                             total_patients=total_patients,
                             total_prescriptions=total_prescriptions,
                             recent_patients=recent_patients,
                             role_color=get_role_color(current_user.role))
    
    elif current_user.role == 'clinic':
        recent_patients = Patient.query.filter_by(created_by=current_user.id).order_by(desc(Patient.created_at)).limit(5).all()
        total_prescriptions = Prescription.query.filter_by(prescribed_by_id=current_user.id).count()
        return render_template('dashboard/clinic.html',
                             total_patients=total_patients,
                             total_prescriptions=total_prescriptions,
                             recent_patients=recent_patients,
                             role_color=get_role_color(current_user.role))
    
    elif current_user.role == 'medical_shop':
        inventory_count = MedicineInventory.query.filter_by(medical_shop_id=current_user.id).count()
        low_stock_items = MedicineInventory.query.filter_by(medical_shop_id=current_user.id).filter(
            MedicineInventory.stock_quantity <= MedicineInventory.reorder_level).count()
        total_sales = Sale.query.filter_by(medical_shop_id=current_user.id).count()
        return render_template('dashboard/medical_shop.html',
                             inventory_count=inventory_count,
                             low_stock_items=low_stock_items,
                             total_sales=total_sales,
                             role_color=get_role_color(current_user.role))

@app.route('/patient/register', methods=['GET', 'POST'])
@login_required
def register_patient():
    if current_user.role not in ['hospital', 'clinic']:
        flash('You do not have permission to register patients.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = PatientRegistrationForm()
    if form.validate_on_submit():
        patient = Patient(
            patient_id=generate_unique_patient_id(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            email=form.email.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            address=form.address.data,
            emergency_contact=form.emergency_contact.data,
            blood_group=form.blood_group.data if form.blood_group.data else None,
            allergies=form.allergies.data,
            medical_history=form.medical_history.data,
            created_by=current_user.id
        )
        
        try:
            db.session.add(patient)
            db.session.commit()
            flash(f'Patient registered successfully! Patient ID: {patient.patient_id}', 'success')
            return redirect(url_for('patient_profile', patient_id=patient.patient_id))
        except Exception as e:
            db.session.rollback()
            flash('Patient registration failed. Please try again.', 'danger')
            app.logger.error(f"Patient registration error: {e}")
    
    return render_template('patient/register.html', form=form)

@app.route('/patient/search', methods=['GET', 'POST'])
@login_required
def search_patient():
    form = PatientSearchForm()
    patient = None
    
    if form.validate_on_submit():
        patient = Patient.query.filter_by(
            patient_id=form.patient_id.data.upper(),
            phone=form.phone.data
        ).first()
        
        if not patient:
            flash('Patient not found or phone number does not match.', 'danger')
        else:
            # Check if user has permission to view this patient
            if current_user.role == 'medical_shop':
                # Medical shops can view any patient for medicine sales
                pass
            elif patient.created_by != current_user.id:
                flash('You do not have permission to view this patient.', 'danger')
                patient = None
    
    return render_template('patient/search.html', form=form, patient=patient)

@app.route('/patient/<patient_id>')
@login_required
def patient_profile(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id.upper()).first_or_404()
    
    # Check permissions
    if current_user.role == 'medical_shop':
        # Medical shops can view any patient for medicine sales
        pass
    elif patient.created_by != current_user.id:
        flash('You do not have permission to view this patient.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get patient's diseases and prescriptions
    diseases = Disease.query.filter_by(patient_id=patient.id).order_by(desc(Disease.created_at)).all()
    prescriptions = Prescription.query.filter_by(patient_id=patient.id).order_by(desc(Prescription.created_at)).all()
    
    return render_template('patient/profile.html', 
                         patient=patient, 
                         diseases=diseases, 
                         prescriptions=prescriptions,
                         calculate_age=calculate_age)

@app.route('/patient/<patient_id>/add_disease', methods=['GET', 'POST'])
@login_required
def add_disease(patient_id):
    if current_user.role not in ['hospital', 'clinic']:
        flash('You do not have permission to add diseases.', 'danger')
        return redirect(url_for('dashboard'))
    
    patient = Patient.query.filter_by(patient_id=patient_id.upper()).first_or_404()
    
    if patient.created_by != current_user.id:
        flash('You do not have permission to modify this patient.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = DiseaseForm()
    if form.validate_on_submit():
        disease = Disease(
            name=form.name.data,
            description=form.description.data,
            diagnosis_date=form.diagnosis_date.data,
            severity=form.severity.data,
            status=form.status.data,
            notes=form.notes.data,
            patient_id=patient.id,
            diagnosed_by=current_user.id
        )
        
        try:
            db.session.add(disease)
            db.session.commit()
            flash('Disease added successfully!', 'success')
            return redirect(url_for('patient_profile', patient_id=patient.patient_id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to add disease. Please try again.', 'danger')
            app.logger.error(f"Add disease error: {e}")
    
    return render_template('patient/add_disease.html', form=form, patient=patient)

@app.route('/patient/<patient_id>/add_prescription', methods=['GET', 'POST'])
@login_required
def add_prescription(patient_id):
    if current_user.role not in ['hospital', 'clinic']:
        flash('You do not have permission to create prescriptions.', 'danger')
        return redirect(url_for('dashboard'))
    
    patient = Patient.query.filter_by(patient_id=patient_id.upper()).first_or_404()
    
    if patient.created_by != current_user.id:
        flash('You do not have permission to create prescriptions for this patient.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = PrescriptionForm()
    if form.validate_on_submit():
        prescription = Prescription(
            prescription_number=generate_unique_prescription_number(),
            patient_id=patient.id,
            prescribed_by_id=current_user.id,
            diagnosis=form.diagnosis.data,
            notes=form.notes.data,
            valid_until=form.valid_until.data
        )
        
        try:
            db.session.add(prescription)
            db.session.commit()
            flash('Prescription created successfully!', 'success')
            return redirect(url_for('prescription_detail', prescription_id=prescription.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to create prescription. Please try again.', 'danger')
            app.logger.error(f"Add prescription error: {e}")
    
    return render_template('patient/add_prescription.html', form=form, patient=patient)

@app.route('/prescription/<int:prescription_id>')
@login_required
def prescription_detail(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    
    # Check permissions
    if current_user.role == 'medical_shop':
        # Medical shops can view any prescription for medicine sales
        pass
    elif prescription.prescribed_by_id != current_user.id:
        flash('You do not have permission to view this prescription.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('prescription/detail.html', prescription=prescription)

@app.route('/medicines')
@login_required
def medicines_list():
    medicines = Medicine.query.all()
    return render_template('medicine/list.html', medicines=medicines)

@app.route('/medicine/add', methods=['GET', 'POST'])
@login_required
def add_medicine():
    form = MedicineForm()
    if form.validate_on_submit():
        medicine = Medicine(
            name=form.name.data,
            generic_name=form.generic_name.data,
            manufacturer=form.manufacturer.data,
            category=form.category.data,
            strength=form.strength.data,
            form=form.form.data,
            price_per_unit=form.price_per_unit.data,
            description=form.description.data,
            side_effects=form.side_effects.data,
            contraindications=form.contraindications.data
        )
        
        try:
            db.session.add(medicine)
            db.session.commit()
            flash('Medicine added successfully!', 'success')
            return redirect(url_for('medicines_list'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to add medicine. Please try again.', 'danger')
            app.logger.error(f"Add medicine error: {e}")
    
    return render_template('medicine/add.html', form=form)

@app.route('/inventory')
@login_required
def inventory():
    if current_user.role != 'medical_shop':
        flash('You do not have permission to view inventory.', 'danger')
        return redirect(url_for('dashboard'))
    
    inventory_items = MedicineInventory.query.filter_by(medical_shop_id=current_user.id).all()
    return render_template('medicine/inventory.html', inventory_items=inventory_items)

@app.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_inventory():
    if current_user.role != 'medical_shop':
        flash('You do not have permission to manage inventory.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = InventoryForm()
    form.medicine_id.choices = [(m.id, f"{m.name} - {m.strength}") for m in Medicine.query.all()]
    
    if form.validate_on_submit():
        inventory = MedicineInventory(
            medicine_id=form.medicine_id.data,
            medical_shop_id=current_user.id,
            stock_quantity=form.stock_quantity.data,
            reorder_level=form.reorder_level.data,
            batch_number=form.batch_number.data,
            expiry_date=form.expiry_date.data,
            cost_price=form.cost_price.data,
            selling_price=form.selling_price.data
        )
        
        try:
            db.session.add(inventory)
            db.session.commit()
            flash('Inventory updated successfully!', 'success')
            return redirect(url_for('inventory'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update inventory. Please try again.', 'danger')
            app.logger.error(f"Add inventory error: {e}")
    
    return render_template('medicine/add_inventory.html', form=form)

# Template filters
@app.template_filter('currency')
def currency_filter(amount):
    return format_currency(amount)

@app.template_filter('age')
def age_filter(birth_date):
    return calculate_age(birth_date)

# Context processors
@app.context_processor
def inject_role_color():
    if current_user.is_authenticated:
        return dict(role_color=get_role_color(current_user.role))
    return dict()

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
