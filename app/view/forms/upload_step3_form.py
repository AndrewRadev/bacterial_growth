from wtforms import (
    BooleanField,
    FieldList,
    FormField,
    SelectMultipleField,
    StringField,
)
from wtforms.validators import DataRequired

from app.view.forms.base_form import BaseForm
from app.model.orm import MeasurementTechnique


class UploadStep3Form(BaseForm):

    class TechniqueForm(BaseForm):
        class Meta:
            csrf = False

        type          = StringField('type', validators=[DataRequired()])
        subjectType   = StringField('subjectType', validators=[DataRequired()])
        units         = StringField('units')
        description   = StringField('description')
        includeStd    = BooleanField('includeStd')
        metaboliteIds = SelectMultipleField('metaboliteIds', choices=[], validate_choice=False)

    techniques = FieldList(FormField(TechniqueForm))

    def validate_techniques(self, field):
        techniques = [
            MeasurementTechnique(type=t['type'], subjectType=t['subjectType'])
            for t in field.data
        ]
        technique_descriptions = [mt.long_name_with_subject_type for mt in techniques]

        self._validate_uniqueness("not unique", technique_descriptions)
