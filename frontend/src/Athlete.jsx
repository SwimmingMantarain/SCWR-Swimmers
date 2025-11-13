import { useSearchParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

function Athlete() {
    const [searchParams] = useSearchParams();
    const id = searchParams.get('id');

    const api_key = import.meta.env.VITE_APIKEY;

    const [athlete, setAthlete] = useState(null);
    const [pbs, setPbs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchAthletes() {
            try {
                const response = await axios.get(`http://localhost:8000/v1/athlete?id=${id}`, {
                    headers: { 'x-api-key': api_key },
                });
                const { athlete, pbs } = response.data;
                setAthlete(athlete);
                setPbs(pbs);
            } catch (err) {
                console.log(err);
                setError("Failed to fetch athlete");
            } finally {
                setLoading(false);
            }
        }
        fetchAthletes();
    }, [api_key]);

    if (loading) return (
        <div id="content">
            {loading && <motion.div animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity }}>Loading...</motion.div>}
        </div>
    )

    if (error) return <div id="content">{error && <div className="text-red-500">{error}</div>}</div>;

    return (
        <div id="content">
            <motion.h1
                className="text-7xl font-bold text-center mb-26 text-yellow-400 select-none"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
            >
                {athlete.first_name} {athlete.last_name}
            </motion.h1>
        </div>
    )
}

export default Athlete;
