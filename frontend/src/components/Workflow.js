import React, { useState } from 'react';

const Workflow = () => {    
    const [response, setResponse] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {                        
            const res = await fetch(`/api/workflow`, {            
                method: 'POST',
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
            <h1>Start Workflow</h1>
            <form onSubmit={handleSubmit}>               
                <button type="submit">Submit</button>
            </form>
            {response && <div>Response: {JSON.stringify(response)}</div>}
        </div>
    );
};

export default Workflow;