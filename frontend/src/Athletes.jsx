import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.02,
            type: "spring",
            stiffness: 90,
            damping: 15,
        },
    },
};

const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
};

function Athletes() {
    const api_key = import.meta.env.VITE_APIKEY;

    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchAthletes() {
            try {
                const response = await axios.get("http://localhost:8000/v1/athletes", {
                    headers: { 'x-api-key': api_key },
                });
                setData(response.data);
            } catch (err) {
                setError("Failed to fetch athletes");
            } finally {
                setLoading(false);
            }
        }
        fetchAthletes();
    }, [api_key]);

    if (loading) return (
        <div id="content">
            {loading && <motion.div animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity }}>Loading...</motion.div>}
        </div>);
    if (error) return <div id="content">{error && <div className="text-red-500">{error}</div>}</div>;

    return (
        <div id="content">
            <motion.h1
                className="text-5xl font-bold text-center mb-26 text-yellow-400 select-none"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
            >
                Athletes
            </motion.h1>
            <motion.ul
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2"
            >
                {data.map(athlete => (
                    <motion.li
                        key={athlete.id}
                        variants={itemVariants}
                        whileHover={{ scale: 1.1, color: '#83B1D5'}}
                        tranition={{ type: 'spring', stiffness: 200, damping: 15 }}
                        className="cursor-pointer select-none"
                    >
                        {athlete.first_name} {athlete.last_name}
                    </motion.li>
                ))}
            </motion.ul>
        </div>
    );
}

export default Athletes;
