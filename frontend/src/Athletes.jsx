import { useEffect, useState } from 'react';
import axios from 'axios';

function Athletes() {
    const api_key = import.meta.env.VITE_APIKEY;

    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchAthletes() {
            try {
                const reponse = await axios.get("http://localhost:8000/v1/athletes", {
                    headers: {
                        'x-api-key': api_key
                    }
                });
                setData(response.data);
            } catch (err) {
                setError("Failed to fetch athletes");
            } finally {
                setLoading(false);
            }
        }
    }, []);

    if (loading) return <div id="content">Loading...</div>;
    if (error) return <div id="content">{error}</div>;

    return (
        <div id="content">
            <h1>Athletes</h1>
            <ul>
                {data.map((athlete) => (
                    <li key={athlete.id}>{athlete.first_name} {athlete.last_name}</li>
                ))}
            </ul>
        </div>
    )
}

export default Athletes
