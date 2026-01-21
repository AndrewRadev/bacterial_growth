Page('.sandbox-page', function($page) {
  $page.find('.js-upload-container-left').customFileInput();
  $page.find('.js-upload-container-right').customFileInput();

  let $leftFileInput  = $('.js-upload-container-left input[type=file]');
  let $rightFileInput = $('.js-upload-container-right input[type=file]');

  let $submitButton = $page.find('input[type=submit]');

  $page.on('change', 'input[type=file]', updateSubmitState)
  $page.on('reset', 'form', function() {
    setTimeout(updateSubmitState, 1);
  });

  updateLogView();
  $page.on('change', '.js-log-left,.js-log-right', updateLogView);

  function updateSubmitState() {
    if ($leftFileInput[0].files.length + $rightFileInput[0].files.length > 0) {
      $submitButton.prop('disabled', false);
    } else {
      $submitButton.prop('disabled', true);
    }
  }

  function updateLogView() {
    let leftType;
    if ($page.find('.js-log-left').is(':checked')) {
      leftType = 'log';
    } else {
      leftType = 'linear';
    }

    let rightType;
    if ($page.find('.js-log-right').is(':checked')) {
      rightType = 'log';
    } else {
      rightType = 'linear';
    }

    $page.find('.js-plotly-plot').each(function() {
      Plotly.relayout(this, {
        'yaxis.type': leftType,
        'yaxis2.type': rightType,
      });
    });
  }
})
