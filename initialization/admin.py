import io
from datetime import datetime, timezone

import simplejson as json
from wtforms import fields
from werkzeug.exceptions import NotFound
from sqlalchemy.orm import configure_mappers
from markupsafe import Markup
from flask import (
    g,
    send_file,
    request,
)
from flask_admin import Admin, form, AdminIndexView, expose
from flask_admin.model.form import converts
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.form import AdminModelConverter
from flask_admin._compat import as_unicode
from flask_admin.model.template import EndpointLinkRowAction

from db import FLASK_DB
from app.model.orm.orm_base import OrmBase
from app.model.orm import (
    Bioreplicate,
    Community,
    Compartment,
    ExcelFile,
    Experiment,
    ExperimentCompartment,
    Measurement,
    MeasurementContext,
    MeasurementTechnique,
    Metabolite,
    ModelingRequest,
    ModelingResult,
    Perturbation,
    Project,
    ProjectUser,
    Strain,
    Study,
    StudyMetabolite,
    StudyTechnique,
    StudyUser,
    Submission,
    SubmissionBackup,
    Taxon,
    User,
)
from app.model.lib.util import humanize_camelcased_string


def json_formatter(_view, data, _name):
    "Format JSON using ``simplejson`` with ``use_decimal=True``"
    return Markup(f"<pre>{json.dumps(data, indent=2, use_decimal=True)}</pre>")


def record_formatter(_view, record, *args):
    "Format ORM records to make them easier to read"
    if hasattr(record, 'publicId'):
        return record.publicId
    elif hasattr(record, 'name'):
        return record.name
    else:
        return str(record)


_FORMATTERS = {
    dict: json_formatter,
    OrmBase: record_formatter,
}


class AppJSONField(fields.TextAreaField):
    "Copied from Flask-admin to replace ``json`` with ``simplejson`` with ``use_decimal=True``"

    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data:
            # prevent utf8 characters from being converted to ascii
            return as_unicode(json.dumps(self.data, use_decimal=True, ensure_ascii=False))
        else:
            return '{}'

    def process_formdata(self, valuelist):
        "Process data received over the wire from a form."

        if valuelist:
            value = valuelist[0]

            # allow saving blank field as None
            if not value:
                self.data = None
                return

            try:
                self.data = json.loads(valuelist[0], use_decimal=True)
            except ValueError:
                raise ValueError(self.gettext('Invalid JSON'))


class AppModelConverter(AdminModelConverter):
    "Custom converter for JSON and datetime fields"

    @converts('JSON')
    def convert_JSON(self, field_args, **extra):
        return AppJSONField(**field_args)

    @converts('UtcDateTime')
    def convert_datetime(self, field_args, **extra):
        return AppDateTimeField(**field_args, default=datetime.utcnow)


class AppDateTimeField(form.DateTimeField):
    "Ensures that timestamps in the database are stored in the UTC timezone"

    def process_formdata(self, valuelist):
        "Process data received over the wire from a form."

        if not valuelist:
            return

        date_str = " ".join(valuelist)
        for format in self.strptime_format:
            try:
                self.data = datetime.strptime(date_str, format).replace(tzinfo=timezone.utc)
                return
            except ValueError:
                self.data = None

        raise ValueError(self.gettext("Not a valid datetime value."))


class AppAdminIndexView(AdminIndexView):
    "Blocks the entire admin for non-admin users"

    @expose('/')
    def index(self):
        if not g.current_user or not g.current_user.isAdmin:
            raise NotFound()
        return super(AppAdminIndexView, self).index()


class AppView(ModelView):
    "Custom view with common functionality for ORM records"

    can_export       = True
    can_view_details = True

    model_form_converter = AppModelConverter
    "Custom converter for JSON and datetime"

    def prettify_name(self, name):
        "Overridden to render camelCased strings nicely in various places"
        return humanize_camelcased_string(name).title()

    column_type_formatters = _FORMATTERS
    "Custom formatters for the list view"

    column_type_formatters_export = _FORMATTERS
    "Custom formatters for the export view"

    column_type_formatters_detail = _FORMATTERS
    "Custom formatters for the detail view"

    def is_accessible(self):
        "Only allow admin users to the admin"
        return g.current_user and g.current_user.isAdmin

    def inaccessible_callback(self, name, **kwargs):
        "Raise 404 instead of 403 to hide the presence of the endpoint for bots"
        raise NotFound()


def init_admin(app):
    """
    Main entry point of the module, initializes Flask-Admin for our Flask app
    """

    configure_mappers()

    admin = Admin(
        app,
        name='μGrowthDB admin',
        index_view=AppAdminIndexView(),
    )

    db_session = FLASK_DB.session

    class StudyView(AppView):
        column_searchable_list = ['name']
        column_exclude_list = ['description']
        form_excluded_columns = [
            'measurements', 'measurementContexts', 'measurementTechniques',
            'studyUsers', 'experiments', 'strains', 'communities', 'compartments',
            'modelingRequests', 'modelingResults', 'bioreplicates',
            'studyMetabolites', 'metabolites',
        ]

    class SubmissionView(AppView):
        column_exclude_list = ['studyDesign', 'dataFile']
        form_excluded_columns = ['project', 'study']

    class ExcelFileView(AppView):
        column_exclude_list         = ['content']
        column_details_exclude_list = ['content']

        can_edit   = False
        can_create = False
        can_export = False

        column_extra_row_actions = [
            EndpointLinkRowAction("fa fa-download", ".download_view"),
        ]

        @expose("/download", methods=("GET",))
        def download_view(self):
            file = g.db_session.get(ExcelFile, request.args['id'])

            return send_file(
                io.BytesIO(file.content),
                as_attachment=True,
                download_name=file.filename
            )

    admin.add_view(AppView(Project,                 db_session, category="Studies"))
    admin.add_view(StudyView(Study,                 db_session, category="Studies"))
    admin.add_view(SubmissionView(Submission,       db_session, category="Studies"))
    admin.add_view(SubmissionView(SubmissionBackup, db_session, category="Studies"))
    admin.add_view(AppView(Strain,                  db_session, category="Studies"))
    admin.add_view(AppView(StudyMetabolite,         db_session, category="Studies"))
    admin.add_view(ExcelFileView(ExcelFile,         db_session, category="Studies"))

    class ExperimentEntityView(AppView):
        # We ignore all of these "child" entities, because they can't
        # practically be updated through the form.
        form_excluded_columns = [
            'bioreplicates',
            'compartments',
            'perturbations',
            'experimentCompartments',
            'experiments',
            'measurementContexts',
            'measurements',
        ]

    admin.add_view(ExperimentEntityView(Experiment,            db_session, category="Experiments"))
    admin.add_view(ExperimentEntityView(ExperimentCompartment, db_session, category="Experiments"))
    admin.add_view(ExperimentEntityView(Compartment,           db_session, category="Experiments"))
    admin.add_view(ExperimentEntityView(Bioreplicate,          db_session, category="Experiments"))
    admin.add_view(ExperimentEntityView(Community,             db_session, category="Experiments"))
    admin.add_view(ExperimentEntityView(Perturbation,          db_session, category="Experiments"))

    class ModelingResultView(AppView):
        column_exclude_list = ['rSummary']

    admin.add_view(AppView(StudyTechnique,            db_session, category="Measurements"))
    admin.add_view(AppView(MeasurementTechnique,      db_session, category="Measurements"))
    admin.add_view(AppView(MeasurementContext,        db_session, category="Measurements"))
    admin.add_view(AppView(Measurement,               db_session, category="Measurements"))
    admin.add_view(AppView(ModelingRequest,           db_session, category="Measurements"))
    admin.add_view(ModelingResultView(ModelingResult, db_session, category="Measurements"))

    class MetaboliteView(AppView):
        column_searchable_list = ['name']
        form_excluded_columns = ['studyMetabolites']

    class TaxonView(AppView):
        column_searchable_list = ['name']

    admin.add_view(MetaboliteView(Metabolite, db_session, category="External data"))
    admin.add_view(TaxonView(Taxon,           db_session, category="External data"))

    class UserView(AppView):
        form_excluded_columns = [
            'createdAt', 'lastLoginAt', 'updatedAt', 'submissions',
            'orcidToken',
            'managedProjects', 'managedStudies',
            'ownedProjects', 'ownedStudies',
            'projectUsers', 'studyUsers',
        ]

    admin.add_view(UserView(User,       db_session, category="Users"))
    admin.add_view(AppView(StudyUser,   db_session, category="Users"))
    admin.add_view(AppView(ProjectUser, db_session, category="Users"))

    return app
