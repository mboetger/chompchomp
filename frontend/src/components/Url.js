import React, { useEffect, useState, useRef } from 'react';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Stack from 'react-bootstrap/Stack';
import Spinner from 'react-bootstrap/Spinner';
import ListGroup from 'react-bootstrap/ListGroup';
import { useParams } from "react-router-dom";
import Container from 'react-bootstrap/Container';

import Domain from './Domain';

const Url = () => {
    const [urlData, setUrlData] = useState({url: null, domain: null});
    const { id } = useParams();
    const idRef = useRef(id);

    useEffect(() => {
        // Fetch the latest URLs from an API endpoint
        fetch(`/api/url/${encodeURI(idRef.current)}`)
            .then(response => response.json())
            .then(urlData => {                                
                const domain = extractDomain(urlData.url);
                fetch(`/api/domain?domain=${encodeURI(domain)}`)
                    .then(response => response.json())
                    .then(data => {
                        setUrlData({url: urlData, domain: data});                        
                    })
                    .catch(error => console.error('Error fetching Domain:', error));
            })
            .catch(error => console.error('Error fetching URLs:', error));                
    }, []);

    const extractDomain = (url) => {
        try {
            const { host } = new URL(url);
            return host.replace(/^www\./, '');
        } catch (error) {
            console.error('Invalid URL:', error);
            return '';
        }
    };

    return (
        <Container>            
            <Stack gap={3}>
                {urlData?.url ? (  
                    <>
                    <h1><a href={urlData?.url?.url}>{urlData?.url?.extract?.title || urlData?.url?.extract?.headline}</a></h1>
                    <h2>By {urlData?.url?.extract?.author !== '' ? urlData?.url?.extract?.author : "Unknown"}</h2>
                    <h6>Article Date: {urlData?.url?.extract?.date || "None"}</h6>
                    <h6>Scanned On: {urlData?.url?.date}</h6>                       
                                 
                <Tabs
                    defaultActiveKey="summary"
                    id="justify-tab-example"
                    className="mb-3"
                    justify
                    >
                    {urlData.url?.summary ? (
                        <Tab eventKey="summary" title="Summary">
                            <p className="lead">{urlData?.url?.summary}</p>
                        </Tab>
                    ) : null}
                    {urlData?.domain ? (
                        <Tab eventKey="domain" title="Domain">
                            <Domain data={urlData?.domain} /> 
                        </Tab>
                    ) : null}                    
                    {urlData?.url.extract?.content ? (
                        <Tab eventKey="content" title="Content">
                            <p className="lead">{urlData?.url?.extract?.content}</p>
                        </Tab>
                    ) : null}                        
                    {urlData?.url.tech ? (
                        <Tab eventKey="tech" title="Tech">
                            <ListGroup>
                            {urlData?.url?.tech.map((technology, index) => (
                                <ListGroup.Item key={index}><h5>{technology.name}</h5></ListGroup.Item>
                            ))}
                            </ListGroup>
                        </Tab>
                    ) : null}   
                    {urlData?.url.keywords ? (
                        <Tab eventKey="keywords" title="Keywords">
                            <ListGroup>
                            {urlData?.url?.keywords.map((keyword, index) => (
                                <ListGroup.Item key={index}><h5><a href={`/?query=${keyword[0]}`}>{keyword[0]}</a></h5></ListGroup.Item>
                            ))}
                            </ListGroup>
                        </Tab>
                    ) : null}                             
                    </Tabs>    
                </>                                  
                ) : 
                <>
                    <div className="d-flex justify-content-center my-4">
                        <Spinner animation="border" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </Spinner>
                    </div>
                </>} 
            </Stack>   
        </Container>     
    );
};

export default Url;