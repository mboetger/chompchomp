import React from 'react';
import './App.css';
import {
    BrowserRouter as Router,  
    Route, Routes,    
  } from "react-router-dom";
import GetUrl from './components/GetUrl';
import PostUrl from './components/PostUrl';
import Workflow from './components/Workflow';
import ChompNav from './components/Nav';
import PostGenerator from './components/PostGenerator';


function App() {
    return (
        <div className="App">
            <ChompNav />  
            <Router>                                                       
                <Routes>
                    <Route path="/urls" element={<GetUrl />} />                                                    
                    <Route path="/workflow" element={<Workflow />} /> 
                    <Route path="/" element={<PostUrl />} />
                    <Route path='/generators' element={<PostGenerator />} />
                </Routes>                                    
            </Router>                            
        </div>
    );
}

export default App;