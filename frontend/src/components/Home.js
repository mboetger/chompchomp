import React from 'react';
import Stack from 'react-bootstrap/Stack';
import Histogram from './Histogram';
import Urls from './Urls';
import Breadcrumb from 'react-bootstrap/Breadcrumb';

const Home = () => {
    return (
        <Stack>
            <Breadcrumb>                
                <Breadcrumb.Item href="https://getbootstrap.com/docs/4.0/components/breadcrumb/">
                    Dataset
                </Breadcrumb.Item>
                <Breadcrumb.Item active>Tech</Breadcrumb.Item>
            </Breadcrumb>
            <Histogram />
            <br />
            <Urls />
        </Stack>        
    );
};

export default Home;