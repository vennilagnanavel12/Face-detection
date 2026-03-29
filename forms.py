from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, IntegerField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('medical_shop', 'Medical Shop')
    ], validators=[DataRequired()])
    organization_name = StringField('Organization Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10, max=500)])
    license_number = StringField('License Number', validators=[DataRequired(), Length(min=5, max=50)])
    submit = SubmitField('Register')

class PatientRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[Optional(), Email()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10, max=500)])
    emergency_contact = StringField('Emergency Contact', validators=[DataRequired(), Length(min=10, max=15)])
    blood_group = SelectField('Blood Group', choices=[
        ('', 'Select Blood Group'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ], validators=[Optional()])
    allergies = TextAreaField('Known Allergies', validators=[Optional()])
    medical_history = TextAreaField('Medical History', validators=[Optional()])
    submit = SubmitField('Register Patient')

class PatientSearchForm(FlaskForm):
    patient_id = StringField('Patient ID', validators=[DataRequired(), Length(min=6, max=6)])
    phone = StringField('Phone Number (for verification)', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Search Patient')

class DiseaseForm(FlaskForm):
    name = StringField('Disease Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    diagnosis_date = DateField('Diagnosis Date', validators=[DataRequired()])
    severity = SelectField('Severity', choices=[
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('recovered', 'Recovered'),
        ('chronic', 'Chronic')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Add Disease')

class MedicineForm(FlaskForm):
    name = StringField('Medicine Name', validators=[DataRequired(), Length(min=2, max=100)])
    generic_name = StringField('Generic Name', validators=[Optional(), Length(max=100)])
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=100)])
    category = StringField('Category', validators=[DataRequired(), Length(min=2, max=50)])
    strength = StringField('Strength', validators=[Optional(), Length(max=50)])
    form = SelectField('Form', choices=[
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
        ('drops', 'Drops'),
        ('inhaler', 'Inhaler')
    ], validators=[DataRequired()])
    price_per_unit = DecimalField('Price per Unit', validators=[Optional(), NumberRange(min=0)])
    description = TextAreaField('Description', validators=[Optional()])
    side_effects = TextAreaField('Side Effects', validators=[Optional()])
    contraindications = TextAreaField('Contraindications', validators=[Optional()])
    submit = SubmitField('Add Medicine')

class PrescriptionForm(FlaskForm):
    diagnosis = TextAreaField('Diagnosis', validators=[DataRequired(), Length(min=10, max=1000)])
    notes = TextAreaField('Notes', validators=[Optional()])
    valid_until = DateField('Valid Until', validators=[DataRequired()])
    submit = SubmitField('Create Prescription')

class PrescriptionMedicineForm(FlaskForm):
    medicine_id = SelectField('Medicine', coerce=int, validators=[DataRequired()])
    dosage = StringField('Dosage', validators=[DataRequired(), Length(min=1, max=50)])
    frequency = SelectField('Frequency', choices=[
        ('once daily', 'Once Daily'),
        ('twice daily', 'Twice Daily'),
        ('thrice daily', 'Thrice Daily'),
        ('four times daily', 'Four Times Daily'),
        ('as needed', 'As Needed'),
        ('every 4 hours', 'Every 4 Hours'),
        ('every 6 hours', 'Every 6 Hours'),
        ('every 8 hours', 'Every 8 Hours'),
        ('every 12 hours', 'Every 12 Hours')
    ], validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired(), Length(min=1, max=50)])
    timing = SelectField('Timing', choices=[
        ('before food', 'Before Food'),
        ('after food', 'After Food'),
        ('with food', 'With Food'),
        ('empty stomach', 'Empty Stomach'),
        ('anytime', 'Anytime')
    ], validators=[Optional()])
    special_instructions = TextAreaField('Special Instructions', validators=[Optional()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Medicine')

class InventoryForm(FlaskForm):
    medicine_id = SelectField('Medicine', coerce=int, validators=[DataRequired()])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    reorder_level = IntegerField('Reorder Level', validators=[DataRequired(), NumberRange(min=1)])
    batch_number = StringField('Batch Number', validators=[Optional(), Length(max=50)])
    expiry_date = DateField('Expiry Date', validators=[Optional()])
    cost_price = DecimalField('Cost Price', validators=[Optional(), NumberRange(min=0)])
    selling_price = DecimalField('Selling Price', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Update Inventory')
