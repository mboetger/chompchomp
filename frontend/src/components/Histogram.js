import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AreaChart, Area, Tooltip, XAxis, ResponsiveContainer } from 'recharts';
import Stack from 'react-bootstrap/Stack';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Button from 'react-bootstrap/Button';


const Histogram = () => {
    const [urls, setSortedUrls] = useState([]);
    const [sortBy, setSortBy] = useState('date_published');
    const [stats, setStats] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        // Fetch the latest URLs from an API endpoint
        fetchUrls(sortBy);
        fetchStats();
    }, [sortBy]);

    const fetchStats = () => {
        fetch('/stats')
            .then(response => response.json())
            .then(data => setStats(data))
            .catch(error => console.error('Error fetching stats:', error));
    };

    const fetchUrls = (sortValue) => {
        fetch(`/histogram?sort_by=${sortValue}`)
            .then(response => response.json())
            .then(data => setSortedUrls(data))
            .catch(error => console.error('Error fetching URLs:', error));
    };

    const handleOnClick = (e) => {
        navigate(`/urls/${e._id}`);
    };

    const handleSort = (sortValue) => {
        setSortBy(sortValue);        
    }

    const removeOutliers = (data) => {
        if (!data || data.length < 4) return data;
      
        const sortedData = [...data].sort((a, b) => a.count - b.count);
        const q1 = sortedData[Math.floor(sortedData.length / 4)].count;
        const q3 = sortedData[Math.floor(sortedData.length * (3 / 4))].count;
        const iqr = q3 - q1;
        const lowerBound = q1 - 1.5 * iqr;
        const upperBound = q3 + 1.5 * iqr;
      
        return data.filter(item => item.count >= lowerBound && item.count <= upperBound);
      }

    return (
        <Stack>
            
            <ResponsiveContainer width="100%" height={100}>
                <AreaChart data={removeOutliers(urls)}>
                    <Area dataKey="count" onClick={handleOnClick}/>
                    <Tooltip />
                    <XAxis dataKey="_id" hide={true} />                
                </AreaChart>        
            </ResponsiveContainer>
            <ButtonGroup aria-label="Dates">
                <Button variant="outline-secondary" onClick={() => handleSort('date_published')}>{stats.urls?.with_date} Dated</Button>
                <Button variant="outline-secondary" onClick={() => handleSort('date_scanned')}>{stats.urls?.count} Scanned</Button>
            </ButtonGroup>
        </Stack>
    );
};

export default Histogram;