import React from 'react';
import ReactToPrint from 'react-to-print';
import Calendar from './components/Calendar.js';
import './App.css';

class ExportPdfComponent extends React.Component {
     
    render() {
      return (
        <div>
          <Calendar ref={(response) => (this.componentRef = response)} />
          
          <ReactToPrint
            content={() => this.componentRef}
            trigger={() => <button className="pdf-btn">Print to PDF!</button>}
          />
        </div>
      );
    }
}
 
export default ExportPdfComponent;