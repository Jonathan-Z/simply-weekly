import React, { Component } from "react";
import $ from 'jquery'; 
class Loop2 extends Component {
  state = {};
  render() {
  return (
    <tbody>
      {() => {
        let rows = [];
        for (let i = 0; i < numrows; i++) {
          rows.push(<ObjectRow key={i}/>);
        }
        return rows;
      }}
    </tbody>
  );
}
export default Header;
