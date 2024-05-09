function parseTimeString(timeString) {
    let timeParts = timeString.split(':');
    let hours = parseInt(timeParts[0]);
    let minutes = parseInt(timeParts[1]);
    let seconds = parseInt(timeParts[2]);

    let parsedDate = new Date(0);
    parsedDate.setHours(hours);
    parsedDate.setMinutes(minutes);
    parsedDate.setSeconds(seconds);

    return parsedDate;
}

function roundToNearest(date, minutes) {
    let coeff = 1000 * 60 * minutes;
    return new Date(Math.round(date.getTime() / coeff) * coeff);
}

function createTimeIntervals(minutes) {
    let intervals = [];
    let nextDate = new Date(0);
    nextDate.setHours(0);
    nextDate.setMinutes(0);
    nextDate.setSeconds(0);

    for (let i = 0; i < (60 / minutes) * 24; i++) {
        intervals.push(nextDate);
        nextDate = new Date(nextDate.getTime() + minutes * 60000);
    }

    return intervals;
}

const chart = document.getElementById("first_time_appointments_chart");
const first_time_appointments = JSON.parse(document.getElementById("first_time_appointments").textContent);
let chart_data = {};

for (const interval of createTimeIntervals(30)) {
    chart_data[interval.toTimeString().slice(0, 5)] = 0;
}

for (const appointment of first_time_appointments) {
    if (appointment.earliest_time_found === null) {
        console.log(appointment);
        continue;
    }
    let appointmentTime = parseTimeString(appointment.earliest_time_found);
    let roundedTime = roundToNearest(appointmentTime, 30);
    chart_data[roundedTime.toTimeString().slice(0, 5)]++;
}

new Chart(chart, {
    type: 'bar',
    data: {
        labels: Object.keys(chart_data),
        datasets: [{
            label: "Termine",
            data: Object.values(chart_data),
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        },
        plugins: {
            title: {
                display: true,
                text: "Wann wurden die Termine erstmalig freigeschaltet?",
                fullSize: false,
            }
        },
    }
});