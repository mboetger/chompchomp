import React from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import LatestUrls from './LatestUrls';
import LatestStats from './LatestStats';

const Home = () => {
    return (
        <Container fluid="md">     
            <Row>
                <Col><LatestStats /></Col>
            </Row>      
            <Row>
                
                <Col><h4>Latest Scans</h4><LatestUrls /></Col>                
            </Row>
        </Container>
    );
};

export default Home;