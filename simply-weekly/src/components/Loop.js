import React, { Component } from "react";
import _ from "lodash";

export default class Loop extends Component {
  render() {
    return (
      <div className="container">
        <ol>
          {_.times(10, (i) => (
            <li key={i}>repeated 3 times</li>
          ))}
        </ol>
      </div>
    );
  }
}