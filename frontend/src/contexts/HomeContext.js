import React, { createContext, useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export const HomeContext = createContext();

export const HomeProvider = ({ children }) => {    
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState('date_published');
    const [dateData, setDateData] = useState({date: null, startDate: null, endDate: null});
    const location = useLocation();

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const query = params.get('query');
        if (query) {
            setSearchQuery(query);
        }
    }, [location]);

    return (
        <HomeContext.Provider value={{ searchQuery, setSearchQuery, sortBy, setSortBy, dateData, setDateData }}>
            {children}
        </HomeContext.Provider>
    );
};