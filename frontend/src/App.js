import React from 'react';
import './App.css';
import PostUrlComponent from './components/PostUrlComponent';
import WorkflowComponent from './components/WorkflowComponent';

function App() {
    return (
        <div className="App">
            <header className="App-header">
                <h1>Chomp Chomp</h1>
                <a href="http://localhost:5555">Workers</a>
            </header>
            <main>
                <p>Gather your data.</p>
                <PostUrlComponent />
                <WorkflowComponent />
            </main>
            <footer>
                <p>Footer content goes here.</p>
            </footer>
        </div>
    );
}

export default App;