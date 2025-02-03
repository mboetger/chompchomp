import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import {
    BrowserRouter as Router,  
    Route, Routes,    
  } from "react-router-dom";
import GetUrl from './GetUrl';
import PostUrl from './PostUrl';
import Workflow from './Workflow';

function ChompNav() {
  return (
    <Navbar expand="lg" className="bg-body-tertiary">
      <Container>
        <Navbar.Brand href="/">Chomp Chomp</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link href="/">Home</Nav.Link>
            <Nav.Link href="/urls">URL</Nav.Link>
            <Nav.Link href="/generators">Generators</Nav.Link>
            <Nav.Link href="/workflow">workflow</Nav.Link>
            <Nav.Link href="http://localhost:5555">Workers</Nav.Link>            
          </Nav>
        </Navbar.Collapse>
      </Container>      
    </Navbar>          
  );
}

export default ChompNav;