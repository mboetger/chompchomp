import React, { useEffect, useState } from 'react';
import Accordion from 'react-bootstrap/Accordion';
import Stack from 'react-bootstrap/esm/Stack';
import Form from 'react-bootstrap/Form';
import { Link } from "react-router-dom";


const Urls = () => {
    const [urls, setUrls] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {        
        fetchUrls(searchQuery);        
    }, [searchQuery]);

    const handleInputChange = (event) => {    
        const query = event.target.value
        setSearchQuery(query);        
    };

    const fetchUrls = (query) => {
        const url = query === '' ? `/urls` : `/urls?query=${encodeURI(query)}`;
        fetch(url)
            .then(response => response.json())
            .then(data => setUrls(data))
            .catch(error => console.error('Error fetching URLs:', error));
    };

    return (
        <Stack>
            <Form.Control
                type="search"
                id="inputSearch"
                aria-describedby="searchHelpBlock"
                onChange={handleInputChange}
            />
            <Form.Text id="searchHelpBlock" muted>
                Search your dataset.
            </Form.Text>
            <Accordion defaultActiveKey="0" flush>
                {urls.map((url, index) => (
                    <Accordion.Item eventKey={index} key={index}>
                        <Accordion.Header><h5>{url.extract?.title || url.extract?.headline}</h5></Accordion.Header>
                        <Accordion.Body>
                            <p>{url.summary || url.extract?.headline}</p>
                            <Link to={`/url/${url._id}`}>View details</Link>
                        </Accordion.Body>
                    </Accordion.Item>                
                ))}
            </Accordion>
        </Stack>
    );
};

export default Urls;