from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    SelectMultipleField,
    IntegerField,
    StringField,
    BooleanField,
    FieldList,
    FormField,
)
from wtforms.validators import DataRequired

# TODO (2024-09-30) Extract types of vessels etc into enums in the database for easy model lookup


class UploadStep3Form(FlaskForm):

    class TechniqueForm(FlaskForm):
        class Meta:
            csrf = False

        type          = StringField('type', validators=[DataRequired()])
        subjectType   = StringField('subjectType', validators=[DataRequired()])
        units         = StringField('units', validators=[DataRequired()])
        description   = StringField('description')
        includeStd    = BooleanField('includeStd')
        metaboliteIds = SelectMultipleField('metaboliteIds')

    vessel_type = SelectField('vessel_type', choices=[
        ('bottles',     "Bottles"),
        ('agar_plates', "Agar plates"),
        ('well_plates', "Well plates"),
        ('mini_react',  "Mini-bioreactors"),
    ], validators=[DataRequired()])

    time_units = SelectField('time_units', choices=[
        ('d', 'Days (d)'),
        ('h', 'Hours (h)'),
        ('m', 'Minutes (m)'),
        ('s', 'Seconds (s)'),
    ])

    bottle_count = IntegerField('bottle_count')
    plate_count  = IntegerField('plate_count')
    column_count = IntegerField('column_count')
    row_count    = IntegerField('row_count')

    timepoint_count = IntegerField('timepoint_count', validators=[DataRequired()])

    techniques = FieldList(FormField(TechniqueForm))
