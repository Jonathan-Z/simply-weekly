let r = document.querySelector(':root');
let times = document.querySelector("#times .time");
let timesStyles = getComputedStyle(times);
let styles = getComputedStyle(document.body);
const calendar = document.querySelector("#holder");
let eventSlots = document.querySelectorAll("#days .day .events");
let div_times = document.querySelector("#times");
let div_days = document.querySelector("#days");
let submit = document.querySelector(".submit-button");
let info = document.querySelector(".text-box input");
let pdfButton = document.querySelector(".pdf-btn");

const { jsPDF } = window.jspdf;

// from https://stackoverflow.com/questions/25946275/exporting-pdf-with-jspdf-not-rendering-css/43064789#43064789
// https://stackoverflow.com/questions/26481645/how-to-use-html2canvas-and-jspdf-to-export-to-pdf-in-a-proper-and-simple-way
if (pdfButton != null) {
    pdfButton.addEventListener("click", () => {
        html2canvas(document.body, {
            allowTaint: true,
            useCORS: true,
        })
        .then(function (canvas) {
            // It will return a canvas element
                let image = canvas.toDataURL("image/png", 0.5);
                pdfButton.setAttribute("href", image);
                pdfButton.setAttribute("download", "calendar.pdf");
                // pdfButton.click();
            window.open(image);
        })
        .catch((e) => {
            // Handle errors
            console.log(e);
        });
          
    });
}


function printPDF() {
    var w = calendar.offsetWidth;
    var h = calendar.offsetHeight;
    html2canvas(calendar, {
    dpi: 300, // Set to 300 DPI
    scale: 3, // Adjusts your resolution
    onrendered: function(canvas) {
        var img = canvas.toDataURL("image/png");
        var doc = new jsPDF('L', 'px', [w, h]);
        doc.addImage(img, 'JPEG', 0, 0, w, h);
        var blobPDF =  new Blob([ doc.output() ], { type : 'application/pdf'});
        var blobUrl = URL.createObjectURL(blobPDF)
        console.log('done')
        pdfButton.setAttribute("href", blobUrl);
        pdfButton.setAttribute("download", "calendar.pdf");
        window.open(blobUrl);
        }
    });
}
    
calendar.addEventListener("click", handleClick);
submit.addEventListener("click", sendToServer);
info.addEventListener("submit", sendToServer);

function sendToServer(e) {
    e.preventDefault();
    console.log(info.value);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "http://127.0.0.1:5000/api/parse?name=simplyWeekly&text=" + info.value, false);
    xmlHttp.send()
    console.log(xmlHttp.responseText);
    let data = JSON.parse(xmlHttp.responseText);
    let toAdd = data.events[data.events.length - 1];
    let date = new Date(toAdd.startTime);
    let day = date.getDay();
    let startTime = (date.getMinutes() + (date.getSeconds() / 60) + (date.getHours() * 60))/30;
    let duration = toAdd.duration / 30;
    let title = toAdd.title;
    // https://css-tricks.com/snippets/javascript/random-hex-color/
    let randomColor = "#" + Math.floor(Math.random() * 16777215).toString(16);
    console.log(date.getMinutes());
    console.log(date.getHours());
    console.log(date.getSeconds());
    console.log(startTime);
    newEvent(day, startTime, duration, title, randomColor);
    info.value = "";
}

function handleClick(e) {
    console.log(e.target);
    if (e != null && (e.target.nodeName == "DIV") && e.target.className == "event") {
        console.log(e.target);
        let event = e.target.querySelector(".label");
        console.log(event.innerText);
        if (event.nodeName == "SPAN") {
            let textReplace = document.createElement("INPUT");
            textReplace.setAttribute("type", "text");
            textReplace.className = "label";
            textReplace.setAttribute("value", event.innerText);
            e.target.replaceChildren();
            e.target.appendChild(textReplace);
            e.target.querySelector(".label").focus();
        }
        else {
            event.blur();
            let textReplace = document.createElement("span");
            textReplace.className = "label";
            textReplace.innerText = event.value;
            e.target.replaceChildren();
            e.target.appendChild(textReplace);
        }
    }
}

// let randButton = document.querySelector("#generateTest");
// randButton.addEventListener("click", () => {
//     randomEvent();
// });

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
    newEvent(day, startTime, duration, "test event", "red");
}

function newEvent(day, start, duration, label, color) {
    const n_event = document.createElement("div");
    n_event.className = "event";
    const n_label = document.createElement("span");

    const p_start = "calc(" + start.toString() + " * var(--cell-height))";
    const p_duration = "calc(" + duration.toString() + " * var(--cell-height))";

    n_event.setAttribute("style", "top: " + p_start + "; height: " + p_duration + "; background-color: " + color);
    n_label.innerText = label;
    n_label.className = "label";
    
    n_event.appendChild(n_label);
    console.log(n_event);
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



init();
// randomEvent();