$(document).ready(function () {

    var $delivery_field = $('#delivery_date')
    //var timeStart = moment();
    //timeStart.minutes(59);
    //timeStart.hour(timeStart.hour() + 1); //min one hour after current time
    
    if($delivery_field.length){
        var timeStart;
        var timeEnd;
        var timeDefault;
        var daysDisabled;
        openerp.jsonRpc("/shop/checkout/get_dates", 'call', {}).then(function(result) {
            //result contains constraints
            //timeStart from result moment([year, month, day, hour, minutes]);
            console.log(result.min_date)
            result.min_date[1] = result.min_date[1] - 1 //moment.js : months start from 0...
            timeStart = moment(result.min_date);
            console.log(timeStart.format("DD/MM hh:mm"))
            timeDefault = moment(timeStart);
            timeDefault.hours(timeDefault.hours() +1);
            timeDefault.minutes(0);
            daysDisabled = result.forbidden_days;
            for (var i = 0; i < daysDisabled.length; i++) {
                daysDisabled[i] = (daysDisabled[i] + 1) % 7 //week starts on sunday
            }
            console.log(daysDisabled)
            //daysOfWeekDisabled from result // Default: [] Accepts: array of numbers from 0-6
            
            console.log(result.max_date)
            result.max_date[1] = result.max_date[1] - 1
            timeEnd = moment(result.max_date);
            
            $delivery_field.datetimepicker({
                    sideBySide: true,
                    enabledHours: [10, 11, 12, 13, 14, 15, 16,17,18], 
                    //TODO : enabledhours relative to shop opening hours
                    minDate : timeStart, //minDate = minDateTime in fact
                    maxDate : timeEnd,
                    daysOfWeekDisabled : daysDisabled,
                    //inline: true,
                    defaultDate: timeDefault,
                    //disabledTimeIntervals: [[moment({ h: 0 }), moment({ h: 8 })], [moment({ h: 18 }), moment({ h: 24 })]],
                    format: 'ddd DD/MM/YYYY HH:mm', //ex : Thu 14/03/2015;
                    stepping: 60 //we choose only hours, but minutes are shown
            }).show(); //.enabledHours([10, 11, 12, 13, 14, 15, 16,17,18]); //enabledHours: [10, 11, 12, 13, 14, 15, 16,17,18],
            //openerp.jsonRpc("/shop/checkout/get_dates", 'call', {}).then(function(result) {
                //result contains constraints
                //timeStart from result moment([year, month, day, hour, minutes]);
                //daysOfWeekDisabled from result // Default: [] Accepts: array of numbers from 0-6
            //});
        });
    }

});
