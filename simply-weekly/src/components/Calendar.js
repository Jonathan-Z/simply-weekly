import React, { Component } from "react";
import "./Calendar.css";
class Calendar extends Component {
  state = {};
  render() {
    return (
      <div className="calendar-container">
        <div id="calendar">
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
                </div>
                <div className="day day2">
                    <span className="label">Tuesday</span>
                </div>
                <div className="day day1">
                    <span className="label">Wednesday</span>
                </div>
                <div className="day day2">
                    <span className="label">Thursday</span>
                </div>
                <div className="day day1">
                    <span className="label">Friday</span>
                </div>
                <div className="day day2">
                    <span className="label">Saturday</span>
                </div>
                <div className="day day1">
                    <span className="label">Sunday</span>
                </div>
            </div>
            <div id="entries">

            </div>
        </div>
      </div>
    );
  }
}

export default Calendar;
