Page('.sandbox-page', function($page) {
  $page.find('.js-upload-container-left').customFileInput();
  $page.find('.js-upload-container-right').customFileInput();

  let $leftFileInput  = $('.js-upload-container-left input[type=file]');
  let $rightFileInput = $('.js-upload-container-right input[type=file]');

  let $submitButton = $page.find('input[type=submit]');

  $page.on('reset', 'form', function() {
    setTimeout(updateSubmitState, 1);
  });
  $page.on('change', 'input[type=file]', updateSubmitState)

  function updateSubmitState() {
    if ($leftFileInput[0].files.length + $rightFileInput[0].files.length > 0) {
      $submitButton.prop('disabled', false);
    } else {
      $submitButton.prop('disabled', true);
    }
  }
})
