import logo from './logo.svg';
import './App.css';
import Header from './components/Header.js';
import Calendar from './components/Calendar.js';
import ExportPdfComponent from './ExportPdfComponent.js';

function App() {
  return (
    <div className="App">
      <Header/>
      <header className="App-header">
      {/* <Calendar/> */}
      <ExportPdfComponent/>
      {/* <h1 className="header-text">SimpleWeekly</h1> */}

        {/* <img src={logo} className="App-logo" alt="logo" /> */}
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
        </a>
      </header>
    </div>
  );
}

export default App;
