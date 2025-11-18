import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.03,
            type: "spring",
            stiffness: 90,
            damping: 15,
        },
    },
};

const cardVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { 
        opacity: 1, 
        y: 0,
        transition: {
            type: "spring",
            stiffness: 100,
            damping: 12
        }
    },
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
        <div className="flex items-center justify-center flex-1 overflow-auto">
            <motion.div 
                animate={{ opacity: [0, 1, 0] }} 
                transition={{ repeat: Infinity, duration: 1.5 }}
                className="text-2xl text-[#83B1D5]"
            >
                Loading...
            </motion.div>
        </div>
    );

    if (error) return (
        <div className="flex items-center justify-center flex-1 overflow-auto">
            <div className="text-red-500 text-xl">{error}</div>
        </div>
    );

    return (
        <div className="flex flex-col flex-1 overflow-auto">
            <motion.div
                className="px-4 pt-6 pb-4"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
            >
                <h1 className="text-4xl md:text-6xl font-bold text-[#F9CE4E] select-none">
                    Athletes
                </h1>
            </motion.div>

            <div className="px-4 md:px-8 pb-8">
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                    className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-3 xl:grid-cols-4 gap-3 md:gap-4 max-w-7xl mx-auto"
                >
                    {data.map((athlete) => (
                        <motion.div
                            key={athlete.id}
                            variants={cardVariants}
                            whileHover={{ 
                                scale: 1.05,
                                y: -8,
                                transition: { type: 'spring', stiffness: 300, damping: 20 }
                            }}
                            whileTap={{ scale: 0.98 }}
                            className="relative cursor-pointer select-none group"
                            onClick={() => navigate(`/athlete?id=${athlete.id}`)}
                        >
                            <div className="relative border-2 border-[#83B1D5] rounded-lg overflow-hidden bg-gradient-to-br from-[#1a2530] to-[#0f1b24] p-4 md:p-6 h-full min-h-[100px] flex items-center justify-center transition-all duration-400 group-hover:border-[#F9CE4E] group-hover:shadow-lg group-hover:shadow-[#83B1D5]/20">
                                <div className="absolute inset-0 bg-[#83B1D5] opacity-0 group-hover:opacity-5 transition-opacity duration-400"></div>
                                
                                <div className="relative z-10 text-center backdrop-blur-sm bg-[#388AC9]/10 rounded-lg p-2 md:p-3 w-full group-hover:bg-[#388AC9]/20 transition-all duration-400">
                                    <div className="text-lg md:text-xl font-bold text-white group-hover:text-[#F9CE4E] transition-colors duration-300">
                                        {athlete.first_name}
                                    </div>
                                    <div className="text-base md:text-lg font-semibold text-[#83B1D5] mt-0.5 group-hover:text-white transition-colors duration-300">
                                        {athlete.last_name}
                                    </div>
                                </div>

                                <div className="absolute top-2 right-2 w-2 h-2 bg-[#F9CE4E] rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                                <div className="absolute bottom-2 left-2 w-2 h-2 bg-[#F9CE4E] rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                            </div>
                        </motion.div>
                    ))}
                </motion.div>
            </div>
        </div>
    );
}

export default Athletes;
