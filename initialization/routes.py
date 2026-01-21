import os

import app.pages.comparison as comparison_pages
import app.pages.excel_files as excel_file_pages
import app.pages.experiments as experiment_pages
import app.pages.help as help_pages
import app.pages.metabolites as metabolite_pages
import app.pages.perturbations as perturbation_pages
import app.pages.projects as project_pages
import app.pages.search as search_pages
import app.pages.static as static_pages
import app.pages.strains as strain_pages
import app.pages.studies as study_pages
import app.pages.modeling as modeling_pages
import app.pages.submissions as submission_pages
import app.pages.upload as upload_pages
import app.pages.users as user_pages
import app.pages.sandbox as sandbox_pages

import app.pages.api as api_pages


def init_routes(app):
    """
    Main entry point of the module.

    Assigns all routes used by the application to handler functions that live
    in ``app.pages``.
    """

    app_env = os.getenv('app_env', 'development')

    #
    # Web routes
    #
    app.add_url_rule("/",       view_func=static_pages.static_home_page)
    app.add_url_rule("/about/", view_func=static_pages.static_about_page)

    app.add_url_rule("/help/",               view_func=help_pages.help_index_page)
    app.add_url_rule("/help/<string:name>/", view_func=help_pages.help_show_page)

    app.add_url_rule("/upload/", view_func=upload_pages.upload_status_page)

    app.add_url_rule("/upload/1", view_func=upload_pages.upload_step1_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/2", view_func=upload_pages.upload_step2_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/3", view_func=upload_pages.upload_step3_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/4", view_func=upload_pages.upload_step4_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/5", view_func=upload_pages.upload_step5_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/6", view_func=upload_pages.upload_step6_page, methods=["GET", "POST"])
    app.add_url_rule("/upload/7", view_func=upload_pages.upload_step7_page, methods=["GET", "POST"])

    app.add_url_rule(
        "/upload/new_submission/",
        view_func=submission_pages.new_submission_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/upload/edit_submission/<id>",
        view_func=submission_pages.edit_submission_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/upload/delete_submission/<id>",
        view_func=submission_pages.delete_submission_action,
        methods=["POST"],
    )

    app.add_url_rule("/upload/data_template.xlsx", view_func=upload_pages.download_data_template_xlsx, methods=["POST"])
    app.add_url_rule(
        "/upload/spreadsheet_preview/",
        view_func=upload_pages.upload_spreadsheet_preview_fragment,
        methods=["POST"],
    )

    app.add_url_rule("/study/<string:publicId>/",                view_func=study_pages.study_show_page)
    app.add_url_rule("/study/<string:publicId>.zip",             view_func=study_pages.study_download_data_zip)
    app.add_url_rule("/study/<string:publicId>/export/",         view_func=study_pages.study_export_page)
    app.add_url_rule("/study/<string:publicId>/export/preview",  view_func=study_pages.study_export_preview_fragment)
    app.add_url_rule("/study/<string:publicId>/manage/",         view_func=study_pages.study_manage_page)
    app.add_url_rule("/study/<string:publicId>/visualize/",      view_func=study_pages.study_visualize_page)
    app.add_url_rule("/study/<string:publicId>/visualize/chart", view_func=study_pages.study_chart_fragment, methods=["POST"])
    app.add_url_rule("/study/<string:publicId>/reset",           view_func=study_pages.study_reset_action,   methods=["POST"])

    app.add_url_rule("/modeling/<string:publicId>/",           view_func=modeling_pages.modeling_page)
    app.add_url_rule("/modeling/<string:publicId>/models.csv", view_func=modeling_pages.modeling_params_csv, methods=["POST"])

    app.add_url_rule(
        "/modeling/<string:publicId>/submit",
        view_func=modeling_pages.modeling_submit_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/modeling/<string:publicId>/toggle-published/<int:modelingResultId>/",
        view_func=modeling_pages.modeling_toggle_published_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/modeling/<string:publicId>/custom-model",
        view_func=modeling_pages.modeling_custom_model_update_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/modeling/<string:publicId>/custom-model/<int:customModelId>/delete",
        view_func=modeling_pages.modeling_custom_model_delete_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/modeling/<string:publicId>/custom-model/<int:customModelId>/upload",
        view_func=modeling_pages.modeling_custom_model_upload_action,
        methods=["POST"],
    )
    app.add_url_rule(
        "/modeling/<string:publicId>/check.json",
        view_func=modeling_pages.modeling_check_json,
    )
    app.add_url_rule(
        "/modeling/<string:publicId>/chart/<int:measurementContextId>/",
        view_func=modeling_pages.modeling_chart_fragment,
    )

    app.add_url_rule("/experiment/<string:publicId>/", view_func=experiment_pages.experiment_show_page)
    app.add_url_rule("/project/<string:publicId>",     view_func=project_pages.project_show_page)

    app.add_url_rule("/strains/completion/",           view_func=strain_pages.taxa_completion_json)
    app.add_url_rule("/metabolites/<string:chebiId>/", view_func=metabolite_pages.metabolite_show_page)
    app.add_url_rule("/metabolites/completion/",       view_func=metabolite_pages.metabolites_completion_json)

    app.add_url_rule("/perturbation/<int:id>", view_func=perturbation_pages.perturbation_show_page)

    app.add_url_rule("/comparison/",      view_func=comparison_pages.comparison_show_page)
    app.add_url_rule("/comparison/chart", view_func=comparison_pages.comparison_chart_fragment, methods=["POST"])
    app.add_url_rule("/comparison/clear", view_func=comparison_pages.comparison_clear_action, methods=["POST"])
    app.add_url_rule(
        "/comparison/update/<action>.json",
        view_func=comparison_pages.comparison_update_json,
        methods=["POST"],
    )

    app.add_url_rule("/search/",          view_func=search_pages.search_index_page)
    app.add_url_rule("/advanced-search/", view_func=search_pages.advanced_search_index_page)

    app.add_url_rule("/profile/", view_func=user_pages.user_show_page)
    app.add_url_rule("/login/",   view_func=user_pages.user_login_page)
    app.add_url_rule("/logout/",  view_func=user_pages.user_logout_action, methods=["POST"])

    if app_env in ('development', 'test'):
        app.add_url_rule("/backdoor/", view_func=user_pages.user_backdoor_page, methods=["GET", "POST"])

    app.add_url_rule("/claim-project/", view_func=user_pages.user_claim_project_action, methods=["POST"])
    app.add_url_rule("/claim-study/",   view_func=user_pages.user_claim_study_action,   methods=["POST"])

    app.add_url_rule("/excel_files/<id>.xlsx", view_func=excel_file_pages.download_excel_file)

    app.add_url_rule(
        "/sandbox/",
        view_func=sandbox_pages.sandbox_index_page,
        methods=["GET", "POST"],
    )

    #
    # API routes
    #
    app.add_url_rule("/api/v1/project/<string:publicId>.json",    view_func=api_pages.project_json)
    app.add_url_rule("/api/v1/study/<string:publicId>.json",      view_func=api_pages.study_json)
    app.add_url_rule("/api/v1/experiment/<string:publicId>.json", view_func=api_pages.experiment_json)
    app.add_url_rule("/api/v1/experiment/<string:publicId>.csv",  view_func=api_pages.experiment_csv)

    app.add_url_rule("/api/v1/measurement-context/<int:id>.json", view_func=api_pages.measurement_context_json)
    app.add_url_rule("/api/v1/measurement-context/<int:id>.csv",  view_func=api_pages.measurement_context_csv)

    app.add_url_rule("/api/v1/bioreplicate/<int:id>.json", view_func=api_pages.bioreplicate_json)
    app.add_url_rule("/api/v1/bioreplicate/<int:id>.csv",  view_func=api_pages.bioreplicate_csv)

    app.add_url_rule("/api/v1/search.json",  view_func=api_pages.search_json)

    return app
