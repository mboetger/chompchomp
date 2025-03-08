import React, { useEffect, useState, useContext } from 'react';
import { AreaChart, Area, Label, Tooltip, XAxis, ResponsiveContainer, ReferenceLine, ReferenceArea } from 'recharts';
import Stack from 'react-bootstrap/Stack';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Button from 'react-bootstrap/Button';
import { HomeContext } from '../contexts/HomeContext';

const Histogram = () => {
    const { sortBy, setSortBy, dateData, setDateData } = useContext(HomeContext);
    const [histogram, setHistogram] = useState([]);    
    const [stats, setStats] = useState([]);    
    const [selecting, setSelecting] = useState(false);

    useEffect(() => {
        // Fetch the latest URLs from an API endpoint
        fetchUrls(sortBy);
        fetchStats();
    }, [sortBy]);

    const fetchStats = () => {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => setStats(data))
            .catch(error => console.error('Error fetching stats:', error));
    };

    const fetchUrls = (sortValue) => {
        fetch(`/api/histogram?sort_by=${sortValue}`)
            .then(response => response.json())
            .then(data => setHistogram(data))
            .catch(error => console.error('Error fetching URLs:', error));
    };

    const handleMouseDown = (e) => {
        setSelecting(true);
        if (e && e.activeLabel !== undefined) {            
            setDateData({date: e.activeLabel, startDate: e.activeLabel, endDate: null});
        }
    };

    const handleMouseUp = (e) => {        
        if (selecting && e && e.activeLabel !== undefined && e.activeLabel !== dateData.startDate) {            
            setDateData({...dateData, date: null, endDate: e.activeLabel});                                        
        }
        setSelecting(false);
    }

    const handleMouseMove = (e) => {        
        if (selecting && dateData.startDate !== null && e && e.activeLabel !== undefined) {            
            setDateData({...dateData, endDate: e.activeLabel, });                      
        }
    };

    const handleSort = (sortValue) => {
        setDateData({date: null, startDate: null, endDate: null});
        setSortBy(sortValue);        
    }

    const sanatize = (data) => {
        if (!data || data.length < 4) return data;
      
        const sortedData = [...data].sort((a, b) => a.count - b.count);
        const q1 = sortedData[Math.floor(sortedData.length / 4)].count;
        const q3 = sortedData[Math.floor(sortedData.length * (3 / 4))].count;
        const iqr = q3 - q1;
        const lowerBound = q1 - 1.5 * iqr;
        const upperBound = q3 + 1.5 * iqr;
      
        return data.filter(item => item.count >= lowerBound && item.count <= upperBound).map(item => ({
            "_id": item._id.split('T')[0],
            "count": item.count,
        }));
    }

    return (
        <Stack>            
            <ResponsiveContainer width="100%" height={100}>
                <AreaChart 
                    data={sanatize(histogram)}                     
                    onMouseDown={handleMouseDown}
                    onMouseMove={handleMouseMove}
                    onMouseUp={handleMouseUp}>
                    <Area dataKey="count"/>
                    <Tooltip wrapperClassName="bg-dark" />
                    <XAxis dataKey="_id" hide={true} />
                    {!selecting && dateData.date !== null && dateData.endDate === null &&
                         <ReferenceLine x={dateData.date} stroke="red" />
                    }
                    {dateData.startDate !== null && dateData.endDate !== null && 
                        <ReferenceArea
                            x1={dateData.startDate}
                            x2={dateData.endDate}
                            fill="red"
                            fillOpacity={0.3}                            
                            label={
                                <Label
                                    value={`${dateData.startDate} - ${dateData.endDate}`}
                                    position="insideTop"
                                    fill="white"
                                    fontSize={18}
                                    fontWeight="bold"
                                />
                            }
                        />
                    }
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