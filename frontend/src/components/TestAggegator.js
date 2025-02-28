import React, { useState } from 'react';

const TestAggegator = () => {
    const [url, setUrl] = useState('');
    const [xpath, setXpath] = useState('');
    const [response, setResponse] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {            
            const body = JSON.stringify({
                url: encodeURIComponent(url),
                xpath: encodeURIComponent(xpath)});     
                
            const res = await fetch(`/api/test/aggregator`, {            
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json;'
                  },
                body: body,
            });
            const data = await res.json();
            setResponse(data);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div>
            <h1>Test Aggregator</h1>
            <form onSubmit={handleSubmit}>
                <label>
                    URL:
                    <input
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                    />
                </label>
                <label>
                    XPath:
                    <input
                        type="text"
                        value={xpath}
                        onChange={(e) => setXpath(e.target.value)}
                    />
                </label>
                <button type="submit">Submit</button>
            </form>
            {response && <div>Response: {JSON.stringify(response)}</div>}
        </div>
    );
};

export default TestAggegator;