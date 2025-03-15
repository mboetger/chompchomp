import React, { useContext } from 'react';
import Stack from 'react-bootstrap/esm/Stack';
import Form from 'react-bootstrap/Form';
import { HomeContext} from '../contexts/HomeContext';


const Search = () => {    
    const { setSearchQuery} = useContext(HomeContext);  

    const handleInputChange = (event) => {          
        const query = event.target.value
        setSearchQuery(query);        
    };

    return (
        <Stack>
            <Form.Control
                type="search"
                id="inputSearch"
                aria-describedby="searchHelpBlock"
                onKeyUp={handleInputChange}                
            />
            <Form.Text id="searchHelpBlock" muted>
                Search your dataset.
            </Form.Text>                            
        </Stack>
    );
};

export default Search;