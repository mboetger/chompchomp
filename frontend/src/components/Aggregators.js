import React from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import TestAggegator from './TestAggegator';
import PostAggegator from './PostAggregator';


const Aggregators = () => {
    return (
        <Container fluid="md">           
            <Row>
                <Col><TestAggegator /></Col>              
                <Col><PostAggegator /></Col>
            </Row>
        </Container>
    );
};

export default Aggregators;