$(document).ready(function () {

    var $delivery_field = $('#delivery_date')
    var timeStart = moment();
    timeStart.minutes(59);
    timeStart.hour(timeStart.hour() + 1); //min one hour after current time
    var timeDefault = moment(timeStart);
    timeDefault.hours(timeDefault.hours() +1);
    timeDefault.minutes(0);
    $delivery_field.datetimepicker({
            sideBySide: true,
            enabledHours: [10, 11, 12, 13, 14, 15, 16,17,18],
            minDate : timeStart, //minDate = minDateTime in fact
            //inline: true,
            defaultDate: timeDefault,
            //disabledTimeIntervals: [[moment({ h: 0 }), moment({ h: 8 })], [moment({ h: 18 }), moment({ h: 24 })]],
            format: 'ddd DD/MM/YYYY HH:mm', //ex : Thu 14/03/2015;
            stepping: 60 //we choose only hours, but minutes are shown
    }).show(); //.enabledHours([10, 11, 12, 13, 14, 15, 16,17,18]); //enabledHours: [10, 11, 12, 13, 14, 15, 16,17,18],
    //openerp.jsonRpc("/shop/checkout/get_dates", 'call', {}).then(function(result) {
        //result contains constraints
        
    //});

});
