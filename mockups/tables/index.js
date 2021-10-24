let r = document.querySelector(':root');
let times = document.querySelector("#times .time");
let timesStyles = getComputedStyle(times);
let styles = getComputedStyle(document.body);
let eventSlots = document.querySelectorAll("#days .day .events");
let div_times = document.querySelector("#times");
let div_days = document.querySelector("#days");
let randButton = document.querySelector("#generateTest");
randButton.addEventListener("click", () => {
    randomEvent();
});

function init() {
    div_times.replaceChildren();
    for (let i = 0; i < 48; i++) {
        let hours = (Math.floor(i / 2) % 12);
        if (i % 24 < 2) hours = 12;
        let minutes = i % 2 == 0 ? "00" : "30";
        let half = i < 24 ? "am" : "pm";
        let time = hours.toString() + ":" + minutes + half;
        createTime(time);
    }
    eventSlots.forEach((e) => {
        e.replaceChildren();
    });
    updateSize();
}

function updateSize() {
    r.style.setProperty("--time-divisions", div_times.childElementCount  );
}

function createTime(time) {
    const n_time = document.createElement("span");
    n_time.className = "time";
    const n_label = document.createElement("span");
    n_label.className = "label";
    n_label.innerText = time;

    n_time.appendChild(n_label);
    div_times.appendChild(n_time);
}

function createDay(dayName, dayDate) {
    const n_day = document.createElement("div");
    n_day.className = "day";
    const n_label = document.createElement("span");
    n_label.className = "label";
    n_label.innerText = (dayName + " " + dayDate).trim();

    n_day.appendChild(n_label);
    div_days.appendChild(n_day);
}

function randomEvent() {
    const cellSize = timesStyles.getPropertyValue("height");
    const cellSizeFormula = styles.getPropertyValue("--cell-height");
    console.log(cellSize);
    console.log(cellSizeFormula);

    const day = Math.floor(Math.random() * 6);
    const startTime = Math.floor(Math.random() * parseInt(styles.getPropertyValue("--time-divisions")));
    const duration = 1 + Math.floor(Math.random() * 5);
    newEvent(day, startTime, duration, "test event", "#6abed8");
};

function newEvent(day, start, duration, label, color) {
    const n_event = document.createElement("div");
    n_event.className = "event";
    const n_label = document.createElement("span");

    const p_start = "calc(" + start.toString() + " * var(--cell-height))";
    const p_duration = "calc(" + duration.toString() + " * var(--cell-height))";

    n_event.setAttribute("style", "top: " + p_start + "; height: " + p_duration + "; background-color: " + color);
    n_label.innerText = label;
    
    n_event.appendChild(n_label);
    eventSlots[day].appendChild(n_event);
}

function updateEvent(n_event, day, start, duration, label, color) {
    const oldStyles = getComputedStyle(n_event);

    let p_start = "calc(" + start.toString() + " * var(--cell-height))";
    let p_duration = "calc(" + duration.toString() + " * var(--cell-height))";
    let n_label = n_event.querySelector("span");

    if (start == null) {
        p_start = oldStyles.getPropertyValue("top");
    }
    if (duration == null) {
        p_duration = oldStyles.getPropertyValue("height");
    }
    if (color == null) {
        color = oldStyles.getPropertyValue("background-color");
    }
    if (label == null) {
        label = n_label.innerText;
    }

    n_event.setAttribute("style", "top: " + p_start + "; height: " + p_duration + "; background-color: " + color);
    n_label.innerText = label;

    if (day != null) {
        eventSlots[day].appendChild(n_event);
    }
}

function handleClick(){
    console.log("hi");

        var xmlHttp = new XMLHttpRequest();

        xmlHttp.open( "GET", "http://127.0.0.1:5000/api/parse?name=SimplyWeekly&text="+encodeURI(document.getElementById("ibox").value), false);
        xmlHttp.send();

        document.getElementById("ibox").value = "";


        const responseData = xmlHttp.response;
        console.log(responseData)
        var duration = 0;
        var title = "";
        var startDate;
        var startMinutes = 0;
        var startDay;
        for (var i=0; i< responseData.events.length; i++) {
            duration = responseData.events[i].duration / 30;
            title = responseData.events[i].title;
            // startDate = Date.parse(responseData.events[i].startTime);
            startDate = new Date(responseData.events[i].startTime);
            startMinutes = startDate.getMinutes() / 30;
            startDay = startDate.getDay();
         }
}

init();