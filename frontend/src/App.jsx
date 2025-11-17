import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

// My shtuff
import './App.css'
import './Mobile.css'

import Header from "./Header"
import Athletes from "./Athletes"
import Athlete from "./Athlete"

function random(length) {
    return Math.floor(Math.random() * length) + 1;
}

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.15,
        },
    },
};

const cardVariants = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: { 
        opacity: 1, 
        scale: 1,
        transition: {
            type: "spring",
            stiffness: 120,
            damping: 15
        }
    },
};

function Home() {
    const navigate = useNavigate();

    return (
        <>
            <motion.div 
                id="content"
                variants={containerVariants}
                initial="hidden"
                animate="visible"
            >
                <motion.div 
                    className="photo-card" 
                    id="card-center"
                    variants={cardVariants}
                    whileHover={{ 
                        scale: 1.02,
                        transition: { type: 'spring', stiffness: 300, damping: 20 }
                    }}
                    whileTap={{ scale: 0.98 }}
                >
                    <div className="card-label-wrapper">
                        <span id="card-label">Club Records</span>
                    </div>
                    <img
                        className="photo-card-img"
                        draggable="false"
                        src={`/img/records-${random(6)}.jpg`}
                        alt="Club Records Image"
                    />
                    
                    {/* Decorative corner dots */}
                    <div className="absolute top-3 right-3 w-2 h-2 bg-[#F9CE4E] rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    <div className="absolute bottom-3 left-3 w-2 h-2 bg-[#F9CE4E] rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </motion.div>
                
                <div id="bottom-row">
                    <motion.div 
                        className="photo-card" 
                        onClick={() => navigate("/athletes")}
                        variants={cardVariants}
                        whileHover={{ 
                            scale: 1.02,
                            transition: { type: 'spring', stiffness: 300, damping: 20 }
                        }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <div className="card-label-wrapper">
                            <span id="card-label">Athletes</span>
                        </div>
                        <img
                            className="photo-card-img"
                            draggable="false"
                            src={`/img/athletes-${random(8)}.jpg`}
                            alt="Athletes Image"
                        />
                        
                        {/* Decorative corner dots */}
                        <div className="absolute top-3 right-3 w-2 h-2 bg-[#F9CE4E] rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div className="absolute bottom-3 left-3 w-2 h-2 bg-[#F9CE4E] rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </motion.div>
                    
                    <motion.div 
                        className="photo-card"
                        variants={cardVariants}
                        whileHover={{ 
                            scale: 1.02,
                            transition: { type: 'spring', stiffness: 300, damping: 20 }
                        }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <div className="card-label-wrapper">
                            <span id="card-label">Competitions</span>
                        </div>
                        <img
                            className="photo-card-img"
                            draggable="false"
                            src={`/img/meets-${random(6)}.jpg`}
                            alt="Meets Image"
                        />
                        
                        {/* Decorative corner dots */}
                        <div className="absolute top-3 right-3 w-2 h-2 bg-[#F9CE4E] rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div className="absolute bottom-3 left-3 w-2 h-2 bg-[#F9CE4E] rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </motion.div>
                </div>
            </motion.div>
        </>
    )
}

function App() {
    return (
        <Router>
            <Header />
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/athletes" element={<Athletes />} />
                <Route path="/athlete" element={<Athlete />} />
            </Routes>
        </Router>
    )
}

export default App
