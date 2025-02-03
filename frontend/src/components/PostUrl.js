import React, { useState } from 'react';

const PostUrl = () => {
    const [itemId, setItemId] = useState('');
    const [response, setResponse] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {            
            const process_url = {url: encodeURIComponent(itemId)};
            const wtf = JSON.stringify(process_url);
            console.log(wtf)
            const res = await fetch(`url`, {            
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json;'
                  },
                body: JSON.stringify(process_url),
            });
            const data = await res.json();
            setResponse(data);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <div>
            <h1>Post URL</h1>
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

export default PostUrl;