Page('.upload-page .step-content.step-6.active', function($step6) {
  let $uploadContainer = $('.js-upload-container');
  // Real file input is outside the container:
  let $fileInput = $('#data-template-input');

  $uploadContainer.customFileInput({ $input: $fileInput });

  $fileInput.on('change', function() {
    submitExcelForm();
  });

  $step6.on('change', '.js-preview select', function() {
    let $select       = $(this);
    let selectedSheet = $select.val().replaceAll(' ', '-');

    $sheets = $(this).parents('.js-preview').find('.js-sheet');
    $sheets.addClass('hidden');

    if (selectedSheet != '') {
      $sheets.filter(`.js-sheet-${selectedSheet}`).removeClass('hidden');
    }
  });

  // Trigger initial sheet preview
  $('.js-preview select').trigger('change');

  function submitExcelForm() {
    let url        = $uploadContainer.prop('action')
    let formData   = new FormData();
    let file       = $fileInput[0].files[0];
    let $preview   = $step6.find('.js-preview');

    formData.append("file", file, file.name);
    $preview.addClass('loading');

    $.ajax({
      type: 'POST',
      url: '/upload/spreadsheet_preview',
      data: formData,
      cache: false,
      contentType: false,
      processData: false,
      success: function(response) {
        $preview.html(response);
        $preview.removeClass('loading');
        $preview.find('select').trigger('change');
      }
    })
  }
});
