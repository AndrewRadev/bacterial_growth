from pathlib import Path
import flask_assets


def init_assets(app):
    """
    Main entry point of the module.

    Initializes Flask-Assets for the Flask app by collecting JavaScript and CSS
    files for compilation and bundling.

    The source JS and CSS files are in app/view, so all paths in this function
    are described relative to the "static/" directory at the root, which holds
    the compiled CSS and JS bundles.
    """

    assets = flask_assets.Environment(app)

    assets.register('app_js', flask_assets.Bundle(
        # External libraries:
        '../app/view/js/vendor/jquery-3.7.1.js',
        '../app/view/js/vendor/jquery.scrollTo-2.1.3.js',
        '../app/view/js/vendor/select2-4.0.13.js',
        '../app/view/js/vendor/popper-core-2.11.8.js',
        '../app/view/js/vendor/tippy-6.3.7.js',
        '../app/view/js/vendor/js-cookie-3.0.5.js',
        '../app/view/js/vendor/underscore-umd-1.13.7.js',
        # Internal libraries:
        '../app/view/js/lib/forms.js',
        '../app/view/js/lib/util.js',
        '../app/view/js/lib/page.js',
        '../app/view/js/lib/tooltips.js',
        '../app/view/js/lib/compare_buttons.js',
        '../app/view/js/lib/custom_file_input.js',
        # Pages:
        '../app/view/js/upload/step1.js',
        '../app/view/js/upload/step2.js',
        '../app/view/js/upload/step3.js',
        '../app/view/js/upload/step4.js',
        '../app/view/js/upload/step5.js',
        '../app/view/js/upload/step6.js',
        '../app/view/js/main.js',
        '../app/view/js/search.js',
        '../app/view/js/export.js',
        '../app/view/js/study.js',
        '../app/view/js/study_visualize.js',
        '../app/view/js/modeling.js',
        '../app/view/js/experiment.js',
        '../app/view/js/comparison.js',
        '../app/view/js/help.js',
        '../app/view/js/sandbox.js',
        filters='rjsmin',
        output='build/app.js'
    ))

    assets.register('plotly_js', flask_assets.Bundle(
        '../app/view/js/vendor/plotly-basic-3.3.1.js',
        output='build/plotly.js'
    ))

    assets.register('katex_js', flask_assets.Bundle(
        '../app/view/js/vendor/katex-0.16.27.js',
        '../app/view/js/vendor/katex-0.16.27-auto-render.js',
        output='build/katex.js'
    ))

    app_css_files = [f"../app/view/css/{p.name}" for p in Path('app/view/css').glob('*.css')]

    assets.register('app_css', flask_assets.Bundle(
        '../app/view/css/vendor/select2-4.0.13.css',
        '../app/view/css/vendor/tippy-fix.css',
        *app_css_files,
        filters='cssmin',
        output='build/app.css'
    ))

    assets.register('katex_css', flask_assets.Bundle(
        '../app/view/css/vendor/katex-0.16.27.css',
        filters='cssmin',
        output='build/katex.css'
    ))

    return app
