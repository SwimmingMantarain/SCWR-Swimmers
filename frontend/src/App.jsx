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

function Home() {
    const navigate = useNavigate();

    return (
        <>
            <div id="content">
                <div class="photo-card" id="card-center">
                    <div class="card-label-wrapper">
                        <span id="card-label">Club Records</span>
                    </div>
                    <img
                        class="photo-card-img"
			draggable="false"
                        src={`/img/records-${random(6)}.jpg`}
                        alt="Club Records Image"></img>
                </div>
                <div id="bottom-row">
                    <div class="photo-card" onClick={() => navigate("/athletes")}>
                        <div class="card-label-wrapper">
                            <span id="card-label">Athletes</span>
                        </div>
                        <img
                            class="photo-card-img"
			draggable="false"
                            src={`/img/athletes-${random(8)}.jpg`}
                            alt="Athletes Image"></img>
                    </div>
                    <div class="photo-card">
                        <div class="card-label-wrapper">
                            <span id="card-label">Competitions</span>
                        </div>
                        <img
                            class="photo-card-img"
			draggable="false"
                            src={`/img/meets-${random(6)}.jpg`}
                            alt="Meets Image"></img>
                    </div>
                </div>
            </div>
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
