import React, { Component } from "react";
import "./Calendar.css";

class Calendar extends Component {
  state = {};
    handleClick(){
        console.log("hi");
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", "http://127.0.0.1:5000/api/parse?name={CalName}&text={calText}", false);
        xmlHttp.send()
  }
  render() {
    return (
      <div className="calendar-container">
        <div id="calendar">
        <div class="text-box">
                <input type="text" placeholder="Type what you want added to calendar"></input>
                <button className="submit-button" onClick={this.handleClick} type="submit">Submit</button>
  </div>
            <div id="times">
                <span className="time time1">
                    <span className="label">7:30am</span>
                </span>
                <span className="time time2">
                    <span className="label">8:00am</span>
                </span>
                <span className="time time1">
                    <span className="label">8:30am</span>
                </span>
                <span className="time time2">
                    <span className="label">9:00am</span>
                </span>
                <span className="time time1">
                    <span className="label">9:30am</span>
                </span>
                <span className="time time2">
                    <span class="label">10:00am</span>
                </span>
                <span className="time time1">
                    <span className="label">10:30am</span>
                </span>
                <span className="time time2">
                    <span className="label">11:00am</span>
                </span>
                <span className="time time1">
                    <span className="label">11:30am</span>
                </span>
            </div>
            <div id="days">
                <div className="day day1">
                    <span className="label">Monday</span>
                    <span className="label event event1 calendar1">Event 1</span>
                    <span className="label event event1 calendar1"></span>

                </div>
                <div className="day day2">
                    <span className="label">Tuesday</span>
                </div>
                <div className="day day1">
                    <span className="label">Wednesday</span>
                    <span className="label"></span>
                    <span className="label event event1 calendar2">Event 2</span>
                    <span className="label event event1 calendar2"></span>
                    <span className="label event event1 calendar2"></span>
                    <span className="label event event1 calendar2"></span>
                    <span className="label event event1 calendar2"></span>
                </div>
                <div className="day day2">
                    <span className="label">Thursday</span>
                </div>
                <div className="day day1">
                    <span className="label">Friday</span>
                    <span className="label event event1 calendar1 eleven-thirty-am ">Event 3</span>
                </div>
                <div className="day day2">
                    <span className="label">Saturday</span>
                </div>
                <div className="day day1">
                    <span className="label">Sunday</span>
                </div>
            </div>
        </div>
      </div>
    );
  }
}
export default Calendar;
