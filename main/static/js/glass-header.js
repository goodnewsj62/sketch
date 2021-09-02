$(function(){
    $(window).scroll(function(event){
        const position = $(window).scrollTop();
        if(position > 10){
            $('header').addClass('glass-effect');
        }else{
            $('header').removeClass('glass-effect');
        }
    });
});