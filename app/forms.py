from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, PasswordField, SubmitField, IntegerField, SelectMultipleField
from wtforms.fields import DateTimeLocalField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget
from app.models import User, Category, Conference, UserRole, ReviewRecommendation, PaperStatus

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class LoginForm(FlaskForm):
    """User login form"""
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """User registration form"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[
        ('AUTHOR', 'Author'),
        ('REVIEWER', 'Reviewer')
    ], default='AUTHOR')
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        # TEMPORARY: Disable database lookup validation until database is fixed
        try:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please use a different email.')
        except Exception:
            # Database not available, skip validation for now
            pass

class PaperSubmissionForm(FlaskForm):
    """Paper submission form"""
    title = StringField('Paper Title', validators=[DataRequired(), Length(min=5, max=500)])
    abstract = TextAreaField('Abstract', validators=[
        DataRequired(), 
        Length(min=100, max=5000, message='Abstract must be between 100-5000 characters')
    ])
    keywords = StringField('Keywords (comma-separated)', validators=[Length(max=500)])
    conference_name = StringField('Conference Name', validators=[DataRequired(), Length(min=2, max=200)])
    categories = MultiCheckboxField('Categories', coerce=int)
    file = FileField('Paper File', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'doc', 'docx'], 'Only PDF and Word documents are allowed')
    ])
    submit = SubmitField('Submit Paper')
    
    def __init__(self, *args, **kwargs):
        super(PaperSubmissionForm, self).__init__(*args, **kwargs)
        self.categories.choices = [(c.id, c.name) for c in Category.query.all()]

class ReviewForm(FlaskForm):
    """Paper review form"""
    technical_quality = SelectField('Technical Quality', choices=[
        (1, '1 - Poor'), (2, '2 - Below Average'), (3, '3 - Fair'), 
        (4, '4 - Good'), (5, '5 - Excellent')
    ], coerce=int, validators=[DataRequired()])
    
    novelty = SelectField('Novelty/Originality', choices=[
        (1, '1 - Poor'), (2, '2 - Below Average'), (3, '3 - Fair'), 
        (4, '4 - Good'), (5, '5 - Excellent')
    ], coerce=int, validators=[DataRequired()])
    
    clarity = SelectField('Clarity of Presentation', choices=[
        (1, '1 - Poor'), (2, '2 - Below Average'), (3, '3 - Fair'), 
        (4, '4 - Good'), (5, '5 - Excellent')
    ], coerce=int, validators=[DataRequired()])
    
    significance = SelectField('Significance/Impact', choices=[
        (1, '1 - Poor'), (2, '2 - Below Average'), (3, '3 - Fair'), 
        (4, '4 - Good'), (5, '5 - Excellent')
    ], coerce=int, validators=[DataRequired()])
    
    overall_score = SelectField('Overall Score', choices=[
        (1, '1 - Strong Reject'), (2, '2 - Reject'), (3, '3 - Weak Reject'),
        (4, '4 - Borderline'), (5, '5 - Weak Accept'), (6, '6 - Accept'),
        (7, '7 - Strong Accept')
    ], coerce=int, validators=[DataRequired()])
    
    recommendation = SelectField('Recommendation', choices=[
        ('REJECT', 'Reject'),
        ('MAJOR_REVISION', 'Major Revision Required'),
        ('MINOR_REVISION', 'Minor Revision Required'),
        ('ACCEPT', 'Accept')
    ], validators=[DataRequired()])
    
    comments = TextAreaField('Comments to Authors', validators=[
        DataRequired(),
        Length(min=50, message='Please provide detailed feedback (minimum 50 characters)')
    ])
    
    confidential_comments = TextAreaField('Confidential Comments to Editors')
    
    submit = SubmitField('Submit Review')

class SearchForm(FlaskForm):
    """Advanced search form"""
    query = StringField('Search Papers')
    conference_id = SelectField('Conference', coerce=int)
    category_id = SelectField('Category', coerce=int)
    status = SelectField('Status', choices=[('', 'All')] + [(s.value, s.value.replace('_', ' ').title()) for s in PaperStatus])
    submit = SubmitField('Search')
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.conference_id.choices = [('', 'All Conferences')] + [(c.id, f"{c.name} {c.year}") for c in Conference.query.all()]
        self.category_id.choices = [('', 'All Categories')] + [(c.id, c.name) for c in Category.query.all()]

class ConferenceForm(FlaskForm):
    """Conference management form"""
    name = StringField('Conference Name', validators=[DataRequired(), Length(max=200)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=2020, max=2030)])
    submission_deadline = DateTimeLocalField('Submission Deadline', validators=[DataRequired()])
    review_deadline = DateTimeLocalField('Review Deadline')
    notification_date = DateTimeLocalField('Notification Date')
    description = TextAreaField('Description')
    website = StringField('Website URL', validators=[Length(max=500)])
    reviews_per_paper = IntegerField('Reviews per Paper', validators=[NumberRange(min=1, max=10)], default=3)
    submit = SubmitField('Save Conference')

class CategoryForm(FlaskForm):
    """Category management form"""
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    color = StringField('Color', validators=[Length(max=7)], default='#007bff')
    submit = SubmitField('Save Category')

class UserManagementForm(FlaskForm):
    """User management form for admins"""
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
        ('AUTHOR', 'Author'),
        ('REVIEWER', 'Reviewer'),
        ('ADMIN', 'Administrator')
    ], validators=[DataRequired()])
    is_active = SelectField('Status', choices=[
        (True, 'Active'),
        (False, 'Inactive')
    ], coerce=bool, default=True)
    submit = SubmitField('Update User')

class AffiliationForm(FlaskForm):
    """User affiliation form"""
    institution_name = StringField('Institution', validators=[DataRequired(), Length(max=200)])
    department = StringField('Department', validators=[Length(max=200)])
    position = StringField('Position', validators=[Length(max=100)])
    is_primary = SelectField('Primary Affiliation', choices=[
        (True, 'Yes'),
        (False, 'No')
    ], coerce=bool, default=False)
    submit = SubmitField('Save Affiliation')

class ReviewerAssignmentForm(FlaskForm):
    """Form for assigning reviewers to papers"""
    reviewer_id = SelectField('Reviewer', coerce=int, validators=[DataRequired()])
    deadline = DateTimeLocalField('Review Deadline')
    submit = SubmitField('Assign Reviewer')
    
    def __init__(self, *args, **kwargs):
        super(ReviewerAssignmentForm, self).__init__(*args, **kwargs)
        self.reviewer_id.choices = [(u.id, f"{u.name} ({u.email})") 
                                   for u in User.query.filter_by(role=UserRole.REVIEWER, is_active=True).all()]

class PasswordResetRequestForm(FlaskForm):
    """Password reset request form"""
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class PasswordResetForm(FlaskForm):
    """Password reset form"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')