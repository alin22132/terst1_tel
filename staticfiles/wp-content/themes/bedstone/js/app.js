(function(window, document){

    var ua = window.navigator.userAgent || '';
    Modernizr.addTest({
        msedge: /Edg[^e]/.test(ua),
        cssvars: window.CSS && CSS.supports('color','var(--test)')
    });

})(window, document);

jQuery(function($) {

    var doc = $(document),
        win = $(window),
        body = $(document.body);

    /* Legacy css vars support */
    if (!Modernizr.cssvars) {
        $.getScript('https://cdn.jsdelivr.net/npm/css-vars-ponyfill@2', function() { cssVars({}); });
    }

    body.on('click', 'a[target="_blank"]', function(e) {
        /* listener to prevent cross-origin links vulnerability */
        $(this).attr('rel', 'noreferrer');
    });


    // ====================================================================
    // Throttle - https://davidwalsh.name/javascript-debounce-function
    // ====================================================================

    function throttle (callback, limit) {
        var wait = false;                  // Initially, we're not waiting
        return function () {               // We return a throttled function
            if (!wait) {                   // If we're not waiting
                callback.call();           // Execute users function
                wait = true;               // Prevent future invocations
                setTimeout(function () {   // After a period of time
                    wait = false;          // And allow future invocations
                }, limit);
            }
        }
    }

    // ====================================================================
    // Debounce -- https://davidwalsh.name/javascript-debounce-function
    // ====================================================================
    // Returns a function, that, as long as it continues to be invoked, will not
    // be triggered. The function will be called after it stops being called for
    // N milliseconds. If `immediate` is passed, trigger the function on the
    // leading edge, instead of the trailing.
    
    function debounce(func, wait, immediate) {
        var timeout;
        return function() {
            var context = this, args = arguments;
            var later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    };

    // ====================================================================
    // Sticky Header
    // ====================================================================
    // Adds and removes classes from <body> and '.site-header'.
    // The classes reference different states possible for the header.
    // .header--visible
    // .header--hide
    // .site-header--sm

    function stickyHeader(){
        var topThreshold = 0;     // distance from top that the full header will display regardless of scroll
        var throttleTime = 250;     // milliseconds to be throttled
        var isVisible = true;       // is the header displayed?
        var isHeaderSmall = false;  // is the header in small mode?
        var $siteHeader = $('.site-header');
        var currentPosition = win.scrollTop(); // set intial position

        //Debounce - Be sure to show header if in topThreshold
        win.on('scroll', debounce(function(){
            if ( win.scrollTop() <= topThreshold ) {
                if ( !isVisible ) {
                    body.addClass('header--visible');
                    body.removeClass('header--hide');
                    isVisible = true;
                }

                if ( isHeaderSmall ) {
                    $siteHeader.removeClass('site-header--sm');
                    isHeaderSmall = false;
                }
            }
        }, 0));


        win.on('scroll', throttle(function(){
            var newPosition = win.scrollTop();

            // When scrolling DOWN the page and past topThreshold
            if ( newPosition > currentPosition && newPosition >= topThreshold ) {
                if ( isVisible ) {
                    body.addClass('header--hide');
                    body.removeClass('header--visible');
                    isVisible = false;
                }
                currentPosition = newPosition;
            }

            //When scrolling UP the page and past topThreshold
            if ( newPosition < currentPosition && newPosition >= topThreshold ) {
                if ( !isVisible ) {
                    body.addClass('header--visible');
                    body.removeClass('header--hide');
                    isVisible = true;
                }
                currentPosition = newPosition;
            }

            // small header handling
            if ( newPosition >= topThreshold && !isHeaderSmall ) {
                $siteHeader.addClass('site-header--sm');
                isHeaderSmall = true;
            } else if ( newPosition <= topThreshold && isHeaderSmall ) {
                $siteHeader.removeClass('site-header--sm');
                isHeaderSmall = false;
            }

        }, throttleTime));

    }
    stickyHeader();  //comment in for a sticky header


    function bedstoneNav()
    {
        var doc = ('undefined' === typeof(doc)) ? $(document) : doc,
            win = ('undefined' === typeof(win)) ? $(window) : win,
            body = ('undefined' === typeof(body)) ? $(document.body) : body,
            nav_main = $('.nav-main__list'),
            toplevels = nav_main.find('.nav-main__item'),
            submenus = nav_main.find('.nav-main__submenu'),
            winWidth = window.innerWidth,
            timeout_resize = null;

        function doResetNav()
        {
            if (winWidth != window.innerWidth) {
                body.removeClass('nav-main--active');
                $('html').removeClass('mobile-menu--active');
                toplevels.removeClass('nav-main__item--active');
                body.removeClass('nav-main-body--active');
                submenus.css('display', '');
                winWidth = window.innerWidth;
            }
        }

        doc
        .on('click', function(e) {
            if (!$(e.target).closest(toplevels).length) {
                toplevels.removeClass('nav-main__item--active');
                body.removeClass('nav-main-body--active');
            }
        });

        body
        .on('click', '.toggle-nav-main', function(e) {
            e.preventDefault();
            body.toggleClass('nav-main--active');
            $('html').toggleClass('mobile-menu--active');
			console.log('test');
        })
        .on('click', '.nav-main__list--primary .nav-main__item a', function(e) {
            var target = $(e.target);
            if (!target.closest(submenus).length) {
                toplevel = target.closest(toplevels);
                if (toplevel.find(submenus).length) {
                    e.preventDefault();
                    if (!body.hasClass('nav-main--active')) {
                        toplevels.not(toplevel).removeClass('nav-main__item--active');
                        body.removeClass('nav-main-body--active');
                    } else {
                        toplevel.find(submenus).slideToggle(300);
                    }
                    $(toplevel).toggleClass('nav-main__item--active');
                    body.toggleClass('nav-main-body--active');
                }
            }
        })
		.on('click', '.nav-main__list--mobile > .menu-item-has-children a', function(e) {
            var target = $(this).attr("data-target");
			body.addClass('nav-main-body--active');
			$('ul[data-submenu = '+target+']').addClass('active');
            console.log(target);
        })
		.on('click', '.nav-main__list--mobile .mobile-sub-menu.active .menu-item-has-children a', function(e) {
            var target = $(this).attr("data-target");
			body.addClass('nav-main-body--active nav-main-body--active-jr');
			$('ul[data-submenu = '+target+']').addClass('active active-jr');
            console.log('abc' + target);
        })
		.on('click', '.menu-item-close-fr a', function(e) {
			var target = $(this).attr("data-target");
			body.removeClass('nav-main-body--active');
			$('ul[data-submenu = '+target+']').removeClass('active');
			console.log('abcdafdfadf');
        })
		.on('click', '.menu-item-close-th a', function(e) {
			var target = $(this).attr("data-target");
			body.removeClass('nav-main-body--active-jr');
			$('ul[data-submenu = '+target+']').removeClass('active');
			console.log('3rd');
        });

        win.resize(function() {
            window.clearTimeout(timeout_resize);
            timeout_resize = window.setTimeout(doResetNav, 200);
        });
    }
    bedstoneNav();

    $(document).keydown(function(e){
        if(e.keyCode == 27) {
            // mobile or zoom
            $('body').removeClass('nav-main--active'); 
            $('html').removeClass('mobile-menu--active'); 
            $('.toggle-nav-main__wrap').attr('aria-expanded','false');

            if(window.outerWidth < 991) {
                $('.toggle-nav-main__wrap').focus();
            }
            // desktop
            $('.nav-main__item--parent').removeClass('nav-main__item--active');
            $('.nav-main__item--parent > a').not(this).attr('aria-expanded','false');

            body.removeClass('nav-main-body--active');
            
        }
    });

    $(document).keyup(function(e){
        if(e.keyCode == 27) {
            $(this).focus();
        }

    });

    $('.sub-menu li:last-child > a').focusout(function(){
        $('.nav-main__item--parent').removeClass('nav-main__item--active');
        body.removeClass('nav-main-body--active');
    });
    $('.megamenu__columns:last-child a:last-child').focusout(function(){
        $('.nav-main__item--parent').removeClass('nav-main__item--active');
        body.removeClass('nav-main-body--active');
    });

    $('.nav-main__item--parent > a').attr('aria-expanded', function (i, val) {
        return val=="false";
    }); 

    $('.nav-main__item--parent > a').click(function () {
        $('.nav-main__item--parent > a').not(this).attr('aria-expanded','false');
    });

    $('.nav-main__item--parent > a').on('click', function (e) {
        var menuItem = $( e.currentTarget );

        if (menuItem.attr( 'aria-expanded') === 'true') {
            $(this).attr( 'aria-expanded', 'false');
        } else {
            $(this).attr( 'aria-expanded', 'true');
        }
    });

     //TOGGLE
    $('.toggle-nav-main__wrap').click(function () {
        $('.toggle-nav-main__wrap').attr('aria-expanded', function (i, val) {
            return val=="false"?true:false;
        });
    });

    $( '.toggle-nav-main__wrap' ).focusin(function() {
        $('body').removeClass('nav-main--active');
        $('html').removeClass('mobile-menu--active'); 
        $(this).attr('aria-expanded','false');
    });

    /* Tables wrap for responsive */
    if ( $('.content table').length ) {
        $('.content table').wrap('<div class="table__wrap"></div>');
    }

    /* Responsive videos */
    if ($.fn.fitVids) {
        $(".site-substance").fitVids();
    }

    /* Legacy media query support */
    if (!Modernizr.mediaqueries) {
        $.getScript('https://cdnjs.cloudflare.com/ajax/libs/respond.js/1.4.2/respond.min.js');
    }

    /* Legacy objectfit support */
    if (!Modernizr.objectfit) {
        $('img.objectfit--contain').each(function(){
            $(this).css('opacity', 0).parent().addClass('objectfit-shiv--contain').css('backgroundImage', 'url(' + this.src + ')');
        });
        $('img.objectfit--cover').each(function(){
            $(this).css('opacity', 0).parent().addClass('objectfit-shiv--cover').css('backgroundImage', 'url(' + this.src + ')');
        });
    };
	
	var tab_counter = 0;
	$('.tab__content').each(function() {
		tab_counter++;
		$(this).addClass('tab__content--' + tab_counter);
		if( tab_counter === 1 ) {
			$(this).addClass('active');
		}
	});
});
