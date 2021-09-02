$(function(){
    $('.mobile-toggle').click(function(){
        $('.sidebar').toggleClass('sidebar-toggle');
        $('.shadow').css('height',($('html').height() - 85));
        $('.shadow').toggle();
        $(this).find('#bars').toggleClass('bar-toggle');
        $(this).find('#close').toggleClass('close-toggle');
    });
});