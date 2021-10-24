import React, { Component } from "react";
import "./Calendar.css";
import { CalFunc } from "../CalFuncs.js";

class Calendar extends Component {
  state = { funcs: null };
    handleClick(){
        console.log("hi");
        var xmlHttp = new XMLHttpRequest();
        xmlHttp.open( "GET", "http://127.0.0.1:5000/api/parse?name={CalName}&text={calText}", false);
        xmlHttp.send();
        const responseData = xmlHttp.response;
        {responseData.map(user => (
        <li key={user.startTime}>{user.startTime}</li>
      ))}
        // xmlHttp.onload = function(){
        //     const responseData = JSON.parse(xmlHttp.responseText);
        //     document.getElementsByClassName('message')[0].innerHTML = JSON.stringify(responseData);
        // }
    }
    
    componentDidMount() {
        // window['init']();
        
    }  

  render() {
    return (
        <div>
            <div className="calendar-container">
                <div className="calendar">
                    <div className="times">
                        <span className="time">
                            <span className="label">7:30am</span>
                        </span>
                        <span className="time">
                            <span className="label">8:00am</span>
                        </span>
                        <span className="time">
                            <span className="label">8:30am</span>
                        </span>
                        <span className="time">
                            <span className="label">9:00am</span>
                        </span>
                        <span className="time">
                            <span className="label">9:30am</span>
                        </span>
                        <span className="time">
                            <span className="label">10:00am</span>
                        </span>
                        <span className="time">
                            <span className="label">10:30am</span>
                        </span>
                        <span className="time">
                            <span className="label">11:00am</span>
                        </span>
                        <span className="time">
                            <span className="label">11:30am</span>
                        </span>
                    </div>
                    
                    <div className="days">
                        <div className="day">
                            <span className="label">Monday</span>
                            <div className="events">
                                <div className="event" style={{ top: "calc(0 * var(--cell-height)", height: "calc(var(--cell-height))", backgroundColor: "gold" }}>
                                    <span>test event</span>
                                </div>
                                <div className="event" style={{ top: "calc(2 * var(--cell-height)", height: "calc(2 * var(--cell-height)", backgroundColor: "tomato" }}>
                                    <span>cool things</span>
                                </div>
                            </div>
                        </div>
                        <div className="day">
                            <span className="label">Tuesday 9/6</span>
                            <div className="events">
                            </div>
                        </div>
                        <div className="day">
                            <span className="label">Wednesday 9/7</span>
                            <div className="events">
                            </div>
                        </div>
                        <div className="day">
                            <span className="label">Thursday 9/8</span>
                            <div className="events">
                            </div>
                        </div>
                        <div className="day">
                            <span className="label">Friday 9/9</span>
                            <div className="events">
                            </div>
                        </div>
                        <div className="day">
                            <span className="label">Saturday 9/10</span>
                            <div className="events">
                            </div>
                        </div>
                        <div className="day">
                            <span className="label">Sunday 9/11</span>
                            <div className="events">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div className="text-box">
                <input type="text" placeholder="Type what you want added to calendar"></input>
                <button className="submit-button" onClick={this.handleClick} type="submit">Submit</button>
            </div>
            <div className="background-print"></div>
        </div>
    );
  }
}
export default Calendar;
