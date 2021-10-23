import React, { Component } from "react";
import './Header.css';
class Header extends Component {
    state = {}
    render(){
        return (
            <div className="container">
            <link href="Header.css" rel="stylesheet"></link>
            <h1 className="header-text">Simply Weekly</h1>
            </div>
        )
    }
}

export default Header;
