import React from 'react';
import Stack from 'react-bootstrap/Stack';
import Histogram from './Histogram';
import { HomeProvider } from '../contexts/HomeContext';
import Urls from './Urls';
import Breadcrumb from 'react-bootstrap/Breadcrumb';
import Search from './Search';

const Home = () => {
    return (
        <Stack>
            <Breadcrumb>                
                <Breadcrumb.Item href="https://getbootstrap.com/docs/4.0/components/breadcrumb/">
                    Dataset
                </Breadcrumb.Item>
                <Breadcrumb.Item active>Tech</Breadcrumb.Item>
            </Breadcrumb>
            <HomeProvider>                
                <Histogram />
                <br />
                <Search />
                <Urls />
            </HomeProvider>
        </Stack>        
    );
};

export default Home;