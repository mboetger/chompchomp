import React, { useState } from 'react';

const GetUrl = () => {
    const [itemId, setItemId] = useState('');
    const [response, setResponse] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {            
            const url = encodeURI(itemId);        
            const res = await fetch(`/url/${url}`, {            
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json;'
                  },
            });
            const data = await res.json();
            setResponse(data);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div>
            <h1>Get URL</h1>
            <form onSubmit={handleSubmit}>
                <label>
                    Item ID:
                    <input
                        type="text"
                        value={itemId}
                        onChange={(e) => setItemId(e.target.value)}
                    />
                </label>
                <button type="submit">Submit</button>
            </form>
            {response && <div>Response: {JSON.stringify(response)}</div>}
        </div>
    );
};

export default GetUrl;