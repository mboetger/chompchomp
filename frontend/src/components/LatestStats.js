import React, { useEffect, useState } from 'react';
import Badge from 'react-bootstrap/Badge';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRefresh } from '@fortawesome/free-solid-svg-icons';
import Col from 'react-bootstrap/esm/Col';
import Row from 'react-bootstrap/esm/Row';
import Container from 'react-bootstrap/Container';


const LatestStats = () => {
    const [stats, setStats] = useState([]);

    useEffect(() => {
        // Fetch the latest URLs from an API endpoint
        const fetchStats = () => {
            fetch('/stats')
                .then(response => response.json())
                .then(data => setStats(data))
                .catch(error => console.error('Error fetching stats:', error));
        };
        fetchStats();
        const intervalId = setInterval(fetchStats, 5000);

        return () => clearInterval(intervalId); // Cleanup on unmount
    }, []);

    const refresh = async (e) => {
        e.preventDefault();
        try {                        
            await fetch(`workflow`, {            
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json;'
                  },                
            });            
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <Container>  
            <Row>
                <Col><h4><Badge bg="secondary">{stats.urls?.count}</Badge></h4></Col>   
                <Col><h4><Badge bg="secondary">{stats.aggregators?.active_count}</Badge></h4></Col>            
                <Col><h4><Badge bg="secondary">{stats.aggregators?.draft_count}</Badge></h4></Col>
            </Row>
            <Row>
                <Col><h4>Urls <FontAwesomeIcon icon={faRefresh} onClick={refresh} /></h4></Col>                                
                <Col><h4>Activate Aggregators</h4></Col>                
                <Col><h4>Draft Aggregators</h4></Col>                
            </Row>                    
        </Container>
    );
};
    

export default LatestStats;