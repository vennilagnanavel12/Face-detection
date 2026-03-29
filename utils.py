import string
import random
from datetime import datetime, timedelta
from models import Patient, Prescription, Sale

def generate_unique_patient_id():
    """Generate a unique 6-character patient ID"""
    while True:
        patient_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not Patient.query.filter_by(patient_id=patient_id).first():
            return patient_id

def generate_unique_prescription_number():
    """Generate a unique prescription number"""
    while True:
        prescription_number = 'RX' + ''.join(random.choices(string.digits, k=8))
        if not Prescription.query.filter_by(prescription_number=prescription_number).first():
            return prescription_number

def generate_unique_sale_number():
    """Generate a unique sale number"""
    while True:
        sale_number = 'SL' + ''.join(random.choices(string.digits, k=8))
        if not Sale.query.filter_by(sale_number=sale_number).first():
            return sale_number

def calculate_age(birth_date):
    """Calculate age from birth date"""
    today = datetime.now().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def get_role_color(role):
    """Get color scheme for user role"""
    colors = {
        'hospital': {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'background': '#f8f9fa',
            'text': '#212529'
        },
        'clinic': {
            'primary': '#28a745',
            'secondary': '#6c757d',
            'background': '#f8f9fa',
            'text': '#212529'
        },
        'medical_shop': {
            'primary': '#fd7e14',
            'secondary': '#6c757d',
            'background': '#f8f9fa',
            'text': '#212529'
        }
    }
    return colors.get(role, colors['hospital'])

def format_currency(amount):
    """Format currency for display"""
    return f"₹{amount:,.2f}"

def get_medicine_form_display(form):
    """Get display name for medicine form"""
    forms = {
        'tablet': 'Tablet',
        'capsule': 'Capsule',
        'syrup': 'Syrup',
        'injection': 'Injection',
        'cream': 'Cream',
        'drops': 'Drops',
        'inhaler': 'Inhaler'
    }
    return forms.get(form, form.title())

def validate_phone_number(phone):
    """Validate phone number format"""
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    # Check if it's a valid Indian phone number
    if len(digits) == 10 and digits[0] in '6789':
        return True
    elif len(digits) == 11 and digits[0] == '0' and digits[1] in '6789':
        return True
    elif len(digits) == 12 and digits[:2] == '91' and digits[2] in '6789':
        return True
    elif len(digits) == 13 and digits[:3] == '+91' and digits[3] in '6789':
        return True
    return False

def get_severity_badge_class(severity):
    """Get Bootstrap badge class for disease severity"""
    severity_classes = {
        'mild': 'badge-success',
        'moderate': 'badge-warning',
        'severe': 'badge-danger'
    }
    return severity_classes.get(severity, 'badge-secondary')

def get_status_badge_class(status):
    """Get Bootstrap badge class for status"""
    status_classes = {
        'active': 'badge-primary',
        'recovered': 'badge-success',
        'chronic': 'badge-warning',
        'fulfilled': 'badge-success',
        'expired': 'badge-danger'
    }
    return status_classes.get(status, 'badge-secondary')
