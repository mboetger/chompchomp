import React, { createContext, useState } from 'react';

export const HomeContext = createContext();

export const HomeProvider = ({ children }) => {    
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState('date_published');
    const [dateData, setDateData] = useState({date: null, startDate: null, endDate: null});

    return (
        <HomeContext.Provider value={{ searchQuery, setSearchQuery, sortBy, setSortBy, dateData, setDateData }}>
            {children}
        </HomeContext.Provider>
    );
};