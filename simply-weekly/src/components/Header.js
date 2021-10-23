import React, { Component } from "react";
// import $ from 'jquery'; 
import "./Header.css";
class Header extends Component {
  state = {};
  render() {
    return (
      <div className="container">
        {/* <div id="preloader" class="loaded">
          <div id="status"></div>
        </div> */}
        <h1 className="header-text">
          <span className="simply">Simply </span>
          <span className="weekly">Weekly</span>
        </h1>
      </div>
    );
  }
}

// $(window).on('load', function(){

// $('#status').fadeOut();
// $('#preloader').delay(350).fadeOut('slow');
// $('#body').delay(350).css({'overflow': 'visible'});

// })
export default Header;
