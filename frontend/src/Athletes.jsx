import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

function Athletes() {
    const api_key = import.meta.env.VITE_APIKEY;

    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchAthletes() {
            try {
                const response = await axios.get("http://localhost:8000/v1/athletes", {
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
        fetchAthletes();
    }, []);

    if (loading) return <div id="content">Loading...</div>;
    if (error) return <div id="content">{error}</div>;

    //const [hoveredID, setHoveredID] = useState(null);

    return (
        <div id="content">
            <motion.h1 
                className="text-5xl font-bold text-center mb-26 text-yellow-400"
                initial={{ opacity: 0, y: -200 }}
                animate={{ opacity: 1, y: 0 }}
            >
                Athletes
            </motion.h1>
            <ul>
                {data.map((athlete) => (
                    <li key={athlete.id}>{athlete.first_name} {athlete.last_name}</li>
                ))}
            </ul>
        </div>
    )
}

export default Athletes
