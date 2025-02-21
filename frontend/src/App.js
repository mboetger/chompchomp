import React from 'react';
import './App.css';
import {
    BrowserRouter as Router,  
    Route, Routes,    
  } from "react-router-dom";
import Home from './components/Home';
import GetUrl from './components/GetUrl';
import Workflows from './components/Workflows';
import ChompNav from './components/Nav';
import Aggregators from './components/Aggregators';
import Url from './components/Url';
import Container from 'react-bootstrap/Container';




function App() {
    return (
        <div className="App">
            <ChompNav />
            <Container>                
                <Router>                                                       
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/urls" element={<GetUrl />} />                                                    
                        <Route path="/workflows" element={<Workflows />} />                     
                        <Route path='/aggregators' element={<Aggregators />} />                    
                        <Route path="/url/:id" element={<Url />} />        

                    </Routes>                                    
                </Router>  
            </Container>                           
        </div>
    );
}

export default App;