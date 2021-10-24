const times = document.querySelector("#times .time");
const timesStyles = getComputedStyle(times);
const styles = getComputedStyle(document.body);
const eventSlots = document.querySelectorAll("#days .day .events");
const randButton = document.querySelector("#generateTest");
randButton.addEventListener("click", () => {
    const cellSize = timesStyles.getPropertyValue("height");
    const cellSizeFormula = styles.getPropertyValue("--cell-height");
    console.log(cellSize);
    console.log(cellSizeFormula);

    const day = Math.floor(Math.random() * 6);
    const startTime = Math.floor(Math.random() * parseInt(styles.getPropertyValue("--time-divisions")));
    const duration = 1 + Math.floor(Math.random() * 5);
    newEvent(day, startTime, duration, "test event", "#6abed8");
});

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