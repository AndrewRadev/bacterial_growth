$(document).ready(function() {
  let currentPath = window.location.pathname;
  let transitionLengthMs = parseInt($(':root').css('--transition-length'), 10);

  $('.nav-links a').each(function() {
    let $link = $(this);
    let $li   = $link.parents('li');
    let href  = $link.attr('href');

    if (href == '/' && currentPath == '/') {
      $li.addClass('current-path');
    } else if (href != '/' && currentPath.startsWith(href)) {
      $li.addClass('current-path');
    }
  });

  // Closing the sidebar
  $('#page-sidebar .close-sidebar-trigger a').on('click', function(e) {
    e.preventDefault();

    $('#page-sidebar').removeClass('open').addClass('closed');
    $('#main .open-sidebar-trigger').addClass('active');
    $('#main').removeClass('with-open-sidebar');

    setTimeout(function() {
      Cookies.set('sidebar-open', false);
      $(document).trigger('x-sidebar-resize')
    }, transitionLengthMs + 1);
  });

  // Opening the sidebar:
  $('#main .open-sidebar-trigger a').on('click', function(e) {
    e.preventDefault();

    $('#page-sidebar').removeClass('closed').addClass('open');
    $('#main .open-sidebar-trigger').removeClass('active');
    $('#main').addClass('with-open-sidebar');

    setTimeout(function() {
      Cookies.set('sidebar-open', true);
      $(document).trigger('x-sidebar-resize')
    }, transitionLengthMs + 1);
  });

  // If there are Plotly plots, resize them automatically:
  $(document).on('x-sidebar-resize', function() {
    $('.js-plotly-plot').each(function() {
      let $chart          = $(this);
      let $chartContainer = $chart.parents('.chart');

      let width = Math.floor($chartContainer.width());

      // Triggered twice, because there seems to be a visual bug with the
      // horizontal legend
      Plotly.relayout($chart[0], { 'width': width });
      Plotly.relayout($chart[0], { 'width': width });
    });
  });

  $('.js-tabs .tab-headers span').on('click', function(e) {
    e.preventDefault();

    let $clickedHeader = $(this);
    let $container = $clickedHeader.parents('.js-tabs')

    let $headers = $container.find('.tab-headers span');
    let $bodies = $clickedHeader.parents('.js-tabs').find('.tab-body');

    $headers.removeClass('active');
    $clickedHeader.addClass('active');

    let clickedIndex = $headers.index(this);
    $bodies.removeClass('active');
    $($bodies[clickedIndex]).addClass('active');
  });

  if (navigator.clipboard) {
    $(document).on('click', '.js-copy-button', function(e) {
      e.preventDefault();

      let $button = $(this);
      let input = $button.next('input');

      navigator.clipboard.writeText(input.val());

      $button.text('Copied ✅');
      $button.prop('disabled', true);

      setTimeout(function () {
        $button.text('Copy 📋');
        $button.prop('disabled', false);
      }, 2000);
    });
  } else {
    // TODO Hide button and just show an input?
  }

  // Open single select2 dropdowns on focus
  // Reference: https://stackoverflow.com/a/49261426
  $(document).on('focus', '.select2-selection.select2-selection--single', function (e) {
    $(this).closest('.select2-container').siblings('select:enabled').select2('open');

    // Note: Hacky, but it doesn't seem like the search input focuses reliably otherwise
    setTimeout(function() {
      $('.select2-container--open .select2-search__field').focus();
    }, 200);
  });

  // Initialize tippy popups:
  initTooltips();

  // On click, smooth-scroll to the location:
  $(document).on('click', '.js-smooth-scroll', function(e) {
    let $link   = $(e.currentTarget);
    let $target = $($link.attr('href'));

    $(document).scrollTo($target, 150, {offset: -20});
  })

  // On click, smooth-scroll to the location:
  $(document).on('click', '.js-scroll-top', function(e) {
    e.preventDefault()
    let $link = $(e.currentTarget);
    $(document).scrollTo(0, 150);

    if (window.history) {
      window.history.pushState(null, null, ' ')
    }
  })
});
