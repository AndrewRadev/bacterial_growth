$(document).ready(function() {
  let $page = $('.upload-page');
  let $step1 = $page.find('.step-content.step-1');
  let $step2 = $page.find('.step-content.step-2');
  let $step3 = $page.find('.step-content.step-3');
  let $step4 = $page.find('.step-content.step-4');

  // Show form corresponding to currently selected submission type
  show_step1_forms($step1.find('.js-submission-type').val());

  // Show form when submission type changes
  $step1.on('change', '.js-submission-type', function() {
    let $select        = $(this);
    let submissionType = $select.val();

    show_step1_forms(submissionType);
  });

  let $multipleStrainSelect = $step2.find('.js-multiple-strain-select');

  $multipleStrainSelect.select2({
    multiple: true,
    width: '100%',
    theme: 'custom',
    ajax: {
      url: '/strains/completion',
      dataType: 'json',
      delay: 100,
      cache: true,
    },
  });

  $multipleStrainSelect.on('change', function() {
    let $form       = $multipleStrainSelect.parents('form');
    let $strainList = $form.find('.strain-list');
    let template    = $form.find('template.strain-list-item').html();
    let selectedIds = new Set($multipleStrainSelect.val());

    $strainList.html('');

    $(this).find('option').each(function() {
      let $option = $(this);
      let name    = $option.text();
      let id      = $option.val();

      if (!selectedIds.has(id)) {
        return;
      }

      let newListItemHtml = template.
        replaceAll('${id}', id).
        replaceAll('${name}', name);

      $strainList.append($(newListItemHtml));
    });
  });

  $multipleStrainSelect.trigger('change');

  $step2.on('click', '.js-add-strain', function(e) {
    e.preventDefault();
    add_new_strain_form($(e.currentTarget), {});
  });

  $step2.on('click', '.js-remove-new-strain', function(e) {
    e.preventDefault();
    $(e.currentTarget).parents('.js-new-strain-container').remove();
  });

  let $metabolitesSelect = $('.js-metabolites-select');

  $metabolitesSelect.select2({
    multiple: true,
    theme: 'custom',
    width: '100%',
    ajax: {
      url: '/metabolites/completion',
      dataType: 'json',
      delay: 100,
      cache: true,
    },
  });
  $metabolitesSelect.trigger('change');

  let $step3form = $step3.find('form');

  $('select[name=vessel_type]').on('change', function() {
    update_vessel_count_inputs();
  });

  update_vessel_count_inputs();

  $step4.on('dragover', '.js-file-upload', function(e) {
    e.preventDefault();
    $(this).addClass('drop-hover');
  });
  $step4.on('dragleave', '.js-file-upload', function(e) {
    e.preventDefault();
    $(this).removeClass('drop-hover');
  });
  $step4.on('drop', '.js-file-upload', function(e) {
    e.preventDefault();

    let $container = $(this).parents('.js-upload-container');
    let $input = $container.find('input[type=file]')
    $input[0].files = e.originalEvent.dataTransfer.files;

    $(this).removeClass('drop-hover');
    submit_excel_form($container);
  });
  $step4.on('change', 'input[type=file]', function(e) {
    let $container = $(this).parents('.js-upload-container');
    submit_excel_form($container);
  });

  function show_step1_forms(submissionType) {
    $forms = $step1.find('.submission-forms form');
    $forms.addClass('hidden');

    if (submissionType != '') {
      $forms.filter(`#form-${submissionType}`).removeClass('hidden');
    }
  }

  function update_strain_list() {
    let $form       = $multipleStrainSelect.parents('form');
    let $strainList = $form.find('.strain-list');
    let template    = $form.find('template.strain-list-item').html();
    let selectedIds = new Set($multipleStrainSelect.val());

    $strainList.html('');

    $(this).find('option').each(function() {
      let $option = $(this);
      let name    = $option.text();
      let id      = $option.val();

      if (!selectedIds.has(id)) {
        return;
      }

      let newListItemHtml = template.
        replaceAll('${id}', id).
        replaceAll('${name}', name);

      $strainList.append($(newListItemHtml));
    });
  }

  initialize_single_strain_select($step2.find('.js-single-strain-select'));

  function add_new_strain_form($addStrainButton, newStrain) {
    // We need to prepend all names and ids with "new-strain-N" for uniqueness:

    let newStrainIndex = $page.find('.js-new-strain-container').length;
    let templateHtml = $page.find('template.new-strain').html();
    let $newForm = $(templateHtml);

    // Modify names:
    $newForm.find('input[name=name]').
      attr('name', `new_strains-${newStrainIndex}-name`);
    $newForm.find('textarea[name=description]').
      attr('name', `new_strains-${newStrainIndex}-description`);
    $newForm.find('select[name=species]').
      attr('name', `new_strains-${newStrainIndex}-species`);

    // Insert into DOM
    $addStrainButton.parents('.form-row').before($newForm);

    // Initialize single-strain selection:
    let $strainSelect = $newForm.find('.js-single-strain-select');
    initialize_single_strain_select($strainSelect);
  }

  function initialize_single_strain_select($select) {
    $select.select2({
      placeholder: 'Select parent species',
      theme: 'custom',
      width: '100%',
      ajax: {
        url: '/strains/completion',
        dataType: 'json',
        delay: 100,
        cache: true,
      },
    });
  }

  function update_vessel_count_inputs() {
    let $vesselTypeInput = $step3form.find('select[name=vessel_type]');
    let vesselType = $vesselTypeInput.val();

    $step3form.find('.vessel-count').addClass('hidden');
    $step3form.find(`.vessel-${vesselType}`).removeClass('hidden');
  }

  function submit_excel_form($container) {
    let url        = $container.prop('action')
    let $preview   = $container.find('.js-preview');
    let $fileInput = $container.find('input[type=file]');
    let formData   = new FormData();
    let file       = $fileInput[0].files[0];

    formData.append("file", file, file.name);

    $.ajax({
      type: 'POST',
      url: '/upload/spreadsheet_preview',
      data: formData,
      cache: false,
      contentType: false,
      processData: false,
      success: function(response) {
        $preview.html(response);

        $preview.find('select').on('change', function() {
          let $select       = $(this);
          let selectedSheet = $select.val();

          // TODO reusable util
          $sheets = $preview.find('.js-sheet');
          $sheets.addClass('hidden');

          if (selectedSheet != '') {
            $sheets.filter(`.js-sheet-${selectedSheet}`).removeClass('hidden');
          }
        });

        $preview.find('select').trigger('change');
      }
    })
  }
});
