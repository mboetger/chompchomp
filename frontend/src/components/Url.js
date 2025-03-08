import React, { useEffect, useState, useRef } from 'react';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Stack from 'react-bootstrap/Stack';
import { useParams } from "react-router-dom";
import Container from 'react-bootstrap/Container';

const Url = () => {
    const [url, setUrl] = useState([]);
    const { id } = useParams();
    const idRef = useRef(id);

    useEffect(() => {
        // Fetch the latest URLs from an API endpoint
        fetch(`/api/url/${encodeURI(idRef.current)}`)
            .then(response => response.json())
            .then(data => setUrl(data))
            .catch(error => console.error('Error fetching URLs:', error));
    }, []);

    return (
        <Container>
            <Stack gap={3}>
                <h1><a href={url.url}>{url.extract?.title || url.extract?.headline}</a></h1>
                <h2>By {url.extract?.author != '' ? url.extract?.author : "Unknown"}</h2>
                <h6>Article Date: {url.extract?.date || "None"}</h6>
                <h6>Scanned On: {url.date}</h6>   
                <Tabs
                    defaultActiveKey="summary"
                    id="justify-tab-example"
                    className="mb-3"
                    justify
                    >
                    {url?.summary ? (
                        <Tab eventKey="summary" title="Summary">
                            <p class="lead">{url.summary}</p>
                        </Tab>
                    ) : null}
                    {url?.extract?.content ? (
                        <Tab eventKey="content" title="Content">
                            <p class="lead">{url.extract?.content}</p>
                        </Tab>
                    ) : null}                        
                    {url?.tech ? (
                        <Tab eventKey="tech" title="Tech">
                            <ul>
                            {url.tech.map((technology, index) => (
                                <li key={index}><h5>{technology.name}</h5></li>
                            ))}
                            </ul>
                        </Tab>
                    ) : null}   
                    {url?.keywords ? (
                        <Tab eventKey="keywords" title="Keywords">
                            <ul>
                            {url.keywords.map((keyword, index) => (
                                <li key={index}><h5>{keyword[0]}</h5></li>
                            ))}
                            </ul>
                        </Tab>
                    ) : null}                             
                </Tabs>    
            </Stack>   
        </Container>     
    );
};

export default Url;