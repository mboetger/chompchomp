import React, { useEffect, useState } from 'react';
import Accordion from 'react-bootstrap/Accordion';
import { Link } from "react-router-dom";


const LatestUrls = () => {
    const [urls, setUrls] = useState([]);

    useEffect(() => {
        // Fetch the latest URLs from an API endpoint
        fetch('/urls')
            .then(response => response.json())
            .then(data => setUrls(data))
            .catch(error => console.error('Error fetching URLs:', error));
    }, []);

    return (
        <Accordion defaultActiveKey="0" flush>
            {urls.map((url, index) => (
                <Accordion.Item eventKey={index} key={index}>
                    <Accordion.Header><h5>{url.extract?.title || url.extract?.headline}</h5></Accordion.Header>
                    <Accordion.Body>
                        <p>{url.summary}</p>

                        <Link to={`/url/${url._id}`}>View details</Link>
                    </Accordion.Body>
                </Accordion.Item>                
            ))}
        </Accordion>
    );
};

export default LatestUrls;