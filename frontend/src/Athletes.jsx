import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
    const navigate = useNavigate();

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
                className="text-7xl font-bold text-center mb-26 text-yellow-400 select-none"
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
                className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5"
            >
                {data.map((athlete, index) => (
                    <motion.li
                        key={athlete.id}
                        variants={itemVariants}
                        whileHover={{ scale: 1.15, color: '#83B1D5'}}
                        transition={{ type: 'spring', stiffness: 200, damping: 25 }}
                        className={`cursor-pointer select-none text-2xl`}
                        onClick={() => navigate(`/athlete?id=${athlete.id}`)}
                    >
                        {athlete.first_name} {athlete.last_name}
                    </motion.li>
                ))}
            </motion.ul>
        </div>
    );
}

export default Athletes;
