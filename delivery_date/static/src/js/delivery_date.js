odoo.define('delivery_date.delivery_date', function (require) {
"use strict";

var ajax = require('web.ajax');


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
        ajax.jsonRpc("/shop/checkout/get_dates", 'call', {}).then(function(result) {
            //result contains constraints
            //timeStart from result moment([year, month, day, hour, minutes]);
            console.log(result.min_date)
            result.min_date[1] = result.min_date[1] - 1 //moment.js : months start from 0...
            timeStart = moment(result.min_date);
            console.log(timeStart.format("DD/MM HH:mm"))
            timeDefault = moment(timeStart);
            timeDefault.hours(timeDefault.hours() +1);
            timeDefault.minutes(0);
            forbidden_intervals_list = result.forbidden_intervals
            console.debug(forbidden_intervals_list)
            console.debug(forbidden_intervals_list.length)
            console.debug(forbidden_intervals_list[0])
            var forbidden_intervals = []
            for (var j = 0; j < forbidden_intervals_list.length; j++){
                forbidden_intervals_list[j][0][1] = forbidden_intervals_list[j][0][1] - 1
                forbidden_intervals_list[j][1][1] = forbidden_intervals_list[j][1][1] - 1
                forbidden_intervals[forbidden_intervals.length] = [moment(forbidden_intervals_list[j][0]), moment(forbidden_intervals_list[j][1])]
                console.log(forbidden_intervals[forbidden_intervals.length - 1][0].format("DD/MM HH:mm"))
            }
            console.debug(forbidden_intervals)
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
                    enabledHours: [10, 11, 12, 13, 14, 15, 16,17,18], //force to check for a valid date at init 
                    //TODO : should check valid date even without that option, and for each day change
                    minDate : timeStart, //minDate is minDateTime in fact
                    maxDate : timeEnd,
                    daysOfWeekDisabled : daysDisabled,
                    //inline: true,
                    defaultDate: timeDefault,
                    format: result.format,//'ddd DD/MM/YYYY HH:mm', //ex : Thu 14/03/2015 10:00
                    stepping: 60, //we choose only hours, but minutes are shown
                    disabledTimeIntervals : forbidden_intervals,
                    inline: true
            }).show();
            console.debug($delivery_field.data("DateTimePicker").date());
            //console.debug(picker.date());
        });
    }

});
});