import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

function ChompNav() {
  return (
    <Navbar expand="lg" bg="dark" variant="dark">
      <Container>
        <Navbar.Brand href="/">Chomp Chomp</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            <Nav.Link href="/">Home</Nav.Link>
            <Nav.Link href="/urls">URL</Nav.Link>
            <Nav.Link href="/aggregators">Aggregators</Nav.Link>
            <Nav.Link href="/workflows">Workflows</Nav.Link>
            <Nav.Link href="http://localhost:5555">Workers</Nav.Link>            
          </Nav>
        </Navbar.Collapse>
      </Container>      
    </Navbar>          
  );
}

export default ChompNav;