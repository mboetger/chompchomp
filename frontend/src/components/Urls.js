import React, { useEffect, useState, useContext } from 'react';
import Accordion from 'react-bootstrap/Accordion';
import { Link } from "react-router-dom";
import { HomeContext} from '../contexts/HomeContext';


const Urls = () => {
    const [urls, setUrls] = useState([]);
    const { searchQuery, sortBy, dateData } = useContext(HomeContext);    

    useEffect(() => {        
        const controller = new AbortController();
        const signal = controller.signal;
        fetchUrls(searchQuery, sortBy, dateData, signal);   
        return () => {
            controller.abort();
        };     
    }, [searchQuery, sortBy, dateData]);

    const fetchUrls = (query, sortBy, dateData, signal) => {
        var url = 'urls';
        if (query) {
            url += `?query=${encodeURI(query)}`;
        }        
        if (sortBy) {
            if (query) {
                url += `&`;
            } else {
                url += `?`;
            }
            url += `sort_by=${sortBy}`;
        }
        if (dateData.date) {
            if (query || sortBy) {
                url += `&`;
            } else {
                url += `?`;
            }
            url += `date=${dateData.date}`;
        }        
        fetch(`/api/${url}`, { signal })
            .then(response => response.json())
            .then(data => setUrls(data))
            .catch(error => {
                if (error.name !== 'AbortError') {                    
                    console.error('Error fetching URLs:', error);
                }
            })
    };

    return (        
        <Accordion defaultActiveKey="0" flush>
            {urls.map((url, index) => (
                <Accordion.Item eventKey={index} key={index}>
                    <Accordion.Header><h5>{url.extract?.title || url.extract?.headline}</h5></Accordion.Header>
                    <Accordion.Body>
                        <p className="lead">{url.summary || url.extract?.headline}</p>
                        <Link to={`/url/${url._id}`}>View details</Link>
                    </Accordion.Body>
                </Accordion.Item>                
            ))}
        </Accordion>                          
    );
};

export default Urls;