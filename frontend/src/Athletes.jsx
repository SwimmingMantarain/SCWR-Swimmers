import { useEffect, useState } from 'react';

function Athletes() {
    const api_key = import.meta.env.VITE_APIKEY;

    const [data, setData] = useState(null);

    useEffect(() => {
        fetch('http://localhost:8000/v1/athletes', {
            headers: {
                'x-api-key': api_key
            }
        })
            .then(res => res.json())
            .then(json => setData(json));
    }, []);

    return (
        <div id="content">
            <p>Poop: {api_key}</p>
            {data ? JSON.stringify(data) : "Pooping..."}
        </div>
    )
}

export default Athletes
