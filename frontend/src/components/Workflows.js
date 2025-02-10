import React from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Workflow from './Workflow';
import Wayback from './Wayback';

const Home = () => {
    return (
        <Container fluid="md">           
            <Row>
                <Col><Workflow /></Col>
                <Col><Wayback /></Col>                
            </Row>
        </Container>
    );
};

export default Home;