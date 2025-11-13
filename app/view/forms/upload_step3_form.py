from wtforms import (
    BooleanField,
    FieldList,
    FormField,
    SelectMultipleField,
    StringField,
)
from wtforms.validators import DataRequired, Length

from app.view.forms.base_form import BaseForm
from app.model.orm import StudyTechnique


class UploadStep3Form(BaseForm):

    class TechniqueForm(BaseForm):
        class Meta:
            csrf = False

        type          = StringField('type',        validators=[DataRequired()])
        subjectType   = StringField('subjectType', validators=[DataRequired()])
        label         = StringField('label',       validators=[Length(max=100)])
        units         = StringField('units')
        description   = StringField('description')
        metaboliteIds = SelectMultipleField('metaboliteIds', choices=[], validate_choice=False)

        includeStd = BooleanField('includeStd')

        includeLive  = BooleanField('includeLive')
        includeDead  = BooleanField('includeDead')
        includeTotal = BooleanField('includeTotal')

    techniques = FieldList(FormField(TechniqueForm))

    def validate_techniques(self, field):
        techniques = [
            StudyTechnique(
                type=t['type'],
                label=t['label'],
                subjectType=t['subjectType'],
            )
            for t in field.data
        ]
        technique_descriptions = [st.long_name_with_subject_type for st in techniques]

        self._validate_uniqueness("not unique", technique_descriptions)
