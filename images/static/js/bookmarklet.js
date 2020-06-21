(function () {
    const jquery_version = '3.4.1';
    const site_url = 'https://127.0.0.1:8000/';
    const static_url = site_url + 'static/';
    const min_width = 100;
    const min_height = 100;

    function bookmarklet(msg) {
        // Load CSS
        let css = jQuery('<link>');
        css.attr({
            rel: 'stylesheet',
            type: 'text/css',
            href: static_url + 'css/bookmarklet.css?r=' + Math.floor(Math.random() * 99999999999999999999)
        });
        jQuery('head').append(css);

        // Load HTML
        let box_html = '<div id="bookmarklet"><a href="#" id="close">&times;</a><h1>Select an image to bookmark:</h1><div class="images"></div></div>';
        jQuery('body').append(box_html);

        jQuery('#bookmarklet #close').click(function () {
            jQuery('#bookmarklet').remove();
        });

        // Find images and display them
        jQuery.each(jQuery('img[src$="jpg"]'), function (index, image) {
            if (jQuery(image).width() >= min_width && jQuery(image).height() >= min_height) {
                let image_url = jQuery(image).attr('src');
                jQuery('#bookmarklet .images').append('<a href="#"><img alt = "Image" src="' + image_url + '" /></a>');
            }
        });

        // When image is selected
        jQuery('#bookmarklet .images a').click(function (e) {
            let selected_image = jQuery(this).children('img').attr('src');
            // Hide bookmarklet
            jQuery('#bookmarklet').hide();
            // Open new window to submit the image
            window.open(site_url + 'images/create/?url='
                + encodeURIComponent(selected_image)
                + '&title='
                + encodeURIComponent(jQuery('title').text()),
                '_blank');
        });
    }

    // Check if jQuery is loaded
    if (typeof window.jQuery != 'undefined') {
        bookmarklet();
    } else {
        // Check for conflicts
        let conflict = typeof window.$ != 'undefined';
        // Create the script and point to Google API
        let script = document.createElement('script');
        script.src = '//ajax.googleapis.com/ajax/libs/jquery/' + jquery_version + '/jquery.min.js';
        // Add the script to the 'head' for processing
        document.head.appendChild(script);
        // Create a way to wait until script loading
        let attempts = 15;
        (function () {
            // Check again if jQuery is undefined
            if (typeof window.jQuery == 'undefined') {
                if (--attempts > 0) {
                    // Calls himself in a few milliseconds
                    window.setTimeout(arguments.callee, 250);
                } else {
                    // Too much attempts to load, send error
                    alert('An error occurred while loading jQuery');
                }
            } else {
                bookmarklet();
            }
        })();
    }
})();