Page('.upload-page .step-content.step-3.active', function($step3) {
  $step3.initAjaxSubform({
    prefixRegex:    /techniques-(\d+)-/,
    prefixTemplate: 'techniques-{}-',

    buildSubform: function (index, $addButton) {
      let templateHtml;

      if ($addButton.is('.js-add-bioreplicate')) {
        templateHtml = $('template.bioreplicate-form').html();
      } else if ($addButton.is('.js-add-strains')) {
        templateHtml = $('template.strain-form').html();
      } else if ($addButton.is('.js-add-metabolites')) {
        templateHtml = $('template.metabolite-form').html();
      }

      let $newForm = $(templateHtml);
      $newForm.addPrefix(`techniques-${index}-`);

      return $newForm;
    },

    initializeSubform: function($subform) {
      let subjectType = $subform.data('subjectType');

      // Specific types of measurements require specific units:
      $subform.on('change', '.js-type-select', function() {
        let $typeSelect = $(this);
        updateUnitSelect($subform, $typeSelect);
      });

      // When the type or unit of measurement change, generate preview:
      $subform.on('change', '.js-preview-trigger', function() {
        updatePreview($subform, subjectType);
      });
      updatePreview($subform, subjectType);

      // If there is a metabolite dropdown, set up its behaviour
      $subform.find('.js-metabolites-select').each(function() {
        let $select = $(this);

        $select.select2({
          multiple: true,
          theme: 'custom',
          width: '100%',
          minimumInputLength: 1,
          ajax: {
            url: '/metabolites/completion/',
            dataType: 'json',
            delay: 100,
            cache: true,
          },
          templateResult: select2Highlighter,
        });

        $select.trigger('change');
      });
    },
  });

  function updateUnitSelect($container, $typeSelect) {
    let $unitsSelect = $container.find('.js-unit-select');
    let type = $typeSelect.val();

    if (type == 'ph' || type == 'od') {
      $unitsSelect.val('');
    } else if (type == '16s') {
      $unitsSelect.val('reads');
    } else if (type == 'plates') {
      $unitsSelect.val('CFUs/mL');
    } else if (type == 'fc') {
      $unitsSelect.val('Cells/mL');
    } else {
    }
  }

  function updatePreview($container, subjectType) {
    let $typeSelect = $container.find('.js-type-select');

    let columnName = $typeSelect.find('option:selected').data('columnName');
    let includeStd = $container.find('.js-include-std').is(':checked');

    let label = $.trim($container.find('.js-label').val())
    if (label == '') {
      label = null;
    } else {
      label = '(' + label + ')'
    }

    let subtypes = [];
    if ($container.find('.js-include-live').is(':checked')) subtypes.push('live');
    if ($container.find('.js-include-dead').is(':checked')) subtypes.push('dead');
    if ($container.find('.js-include-total').is(':checked')) subtypes.push('total');

    let subject = null;

    if (subjectType == 'bioreplicate') {
      subject = 'Community';
    } else if (subjectType == 'strain') {
      subject = '&lt;strain name&gt;';
    } else if (subjectType == 'metabolite') {
      subject = '&lt;metabolite name&gt;';
      columnName = null;
    }

    let columnNames = []

    if (subtypes.length == 0) {
      columnNames.push([subject, columnName, label].filter(Boolean).join(' '));
    } else {
      for (let subtype of subtypes) {
        columnNames.push([subject, subtype, columnName, label].filter(Boolean).join(' '));
      }
    }

    let previewTableHeader = [];
    let previewTableBody   = [];

    previewTableHeader.push('<th>...</th>');
    previewTableBody.push('<td>...</td>');

    for (let columnName of columnNames) {
      previewTableHeader.push(`<th>${columnName}</th>`);
      previewTableBody.push('<td align="center">...</td>');

      if (includeStd) {
        let stdColumnName = [columnName, 'STD'].filter(Boolean).join(' ');

        previewTableHeader.push(`<th>${stdColumnName}</th>`);
        previewTableBody.push('<td align="center">...</td>');
      }
    }

    previewTableHeader.push('<th>...</th>');
    previewTableBody.push('<td>...</td>');

    $container.find('.js-preview-header').html(previewTableHeader.join("\n"));
    $container.find('.js-preview-body').html(previewTableBody.join("\n"));
  }
});
