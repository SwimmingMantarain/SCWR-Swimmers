import { useSearchParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const api_base_url = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const formatTime = (timeStr) => {
  if (!timeStr) return '--:--:--';
  
  const [hms, fraction = '00000'] = timeStr.split('.');
  const [h, m, s] = hms.split(':').map(Number);
  
  const millis = String(Math.round(parseInt(fraction.slice(0, 2), 10))).padStart(2, '0');
  
  if (h > 0) {
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${millis}`;
  } else if (m > 0) {
    return `${m}:${String(s).padStart(2, '0')}.${millis}`;
  } else {
    return `${s}.${millis}`;
  }
};

// Utility function to format date
const formatDate = (dateStr) => {
    if (!dateStr) return '--/--/----';
    const date = new Date(dateStr);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
};

// Group PBs by stroke type
const groupByStroke = (pbs) => {
    const groups = {};
    
    pbs.forEach(pb => {
        const event = pb.event.toLowerCase();
        let stroke = 'Other';
        
        if (event.includes('free')) stroke = 'Freestyle';
        else if (event.includes('back')) stroke = 'Backstroke';
        else if (event.includes('breast')) stroke = 'Breaststroke';
        else if (event.includes('fly') || event.includes('butter')) stroke = 'Butterfly';
        else if (event.includes('medley') || event.includes('im')) stroke = 'Medley';
        
        if (!groups[stroke]) {
            groups[stroke] = [];
        }
        groups[stroke].push(pb);
    });
    
    // Sort each group by event distance
    Object.keys(groups).forEach(stroke => {
        groups[stroke].sort((a, b) => {
            const distA = parseInt(a.event.match(/\d+/)?.[0] || '0');
            const distB = parseInt(b.event.match(/\d+/)?.[0] || '0');
            return distA - distB;
        });
    });
    
    return groups;
};

// Chevron icons
const ChevronDown = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="6 9 12 15 18 9"></polyline>
    </svg>
);

const ChevronUp = () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="18 15 12 9 6 15"></polyline>
    </svg>
);

function StrokeSection({ stroke, pbs, isOpen, onToggle }) {
    const strokeColors = {
        'Freestyle': 'border-blue-400',
        'Backstroke': 'border-purple-400',
        'Breaststroke': 'border-green-400',
        'Butterfly': 'border-yellow-400',
        'Medley': 'border-orange-400',
        'Other': 'border-gray-400'
    };
    
    const color = strokeColors[stroke] || strokeColors['Other'];
    
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`border-2 ${color} rounded-lg overflow-hidden bg-[#1a2530]`}
        >
            <button
                onClick={onToggle}
                className="w-full px-4 py-3 md:px-6 md:py-4 flex items-center justify-between hover:bg-[#243540] transition-colors"
            >
                <div className="flex items-center gap-4">
                    <h2 className="text-xl md:text-2xl font-bold text-[#83B1D5]">{stroke}</h2>
                </div>
                <span className="text-[#83B1D5]">
                    {isOpen ? <ChevronUp /> : <ChevronDown />}
                </span>
            </button>
            
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="overflow-hidden"
                    >
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-[#0f1b24] border-b-2 border-[#83B1D5]">
                                    <tr>
                                        <th className="px-3 py-2 md:px-6 md:py-3 text-[#F9CE4E] font-semibold text-sm md:text-base">Event</th>
                                        <th className="px-3 py-2 md:px-6 md:py-3 text-[#F9CE4E] font-semibold text-sm md:text-base">Course</th>
                                        <th className="px-3 py-2 md:px-6 md:py-3 text-[#F9CE4E] font-semibold text-sm md:text-base">Time</th>
                                        <th className="px-3 py-2 md:px-6 md:py-3 text-[#F9CE4E] font-semibold text-sm md:text-base hidden md:table-cell">Points</th>
                                        <th className="px-3 py-2 md:px-6 md:py-3 text-[#F9CE4E] font-semibold text-sm md:text-base">Date</th>
                                        <th className="px-3 py-2 md:px-6 md:py-3 text-[#F9CE4E] font-semibold text-sm md:text-base hidden md:table-cell">Meet</th>
                                        <th className="px-3 py-2 md:px-6 md:py-3 text-[#F9CE4E] font-semibold text-sm md:text-base">City</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {pbs.map((pb, index) => (
                                        <motion.tr
                                            key={pb.id}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: index * 0.05 }}
                                            className="border-b border-[#2a3540] hover:bg-[#243540] transition-colors"
                                        >
                                            <td className="px-3 py-2 md:px-6 md:py-4 text-white font-medium text-sm md:text-base">{pb.event}</td>
                                            <td className="px-3 py-2 md:px-6 md:py-4">
                                                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                                    pb.course === 25 ? 'bg-blue-900 text-blue-200' : 'bg-green-900 text-green-200'
                                                }`}>
                                                    {pb.course === 25 ? '25m' : '50m'}
                                                </span>
                                            </td>
                                            <td className="px-3 py-2 md:px-6 md:py-4 text-white font-mono text-sm md:text-base">{formatTime(pb.time)}</td>
                                            <td className="px-3 py-2 md:px-6 md:py-4 text-[#83B1D5] font-semibold text-sm md:text-base hidden md:table-cell">{pb.pts}</td>
                                            <td className="px-3 py-2 md:px-6 md:py-4 text-gray-300 text-sm md:text-base">{formatDate(pb.date)}</td>
                                            <td className="px-3 py-2 md:px-6 md:py-4 text-gray-300 max-w-xs truncate text-sm md:text-base hidden md:table-cell" title={pb.meet_name}>
                                                {pb.meet_name}
                                            </td>
                                            <td className="px-3 py-2 md:px-6 md:py-4 text-gray-300 text-sm md:text-base">{pb.city}</td>
                                        </motion.tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}

function Athlete() {
    const [searchParams] = useSearchParams();
    const id = searchParams.get('id');
    
    const api_key = import.meta.env.VITE_APIKEY;
    
    const [athlete, setAthlete] = useState(null);
    const [groupedPbs, setGroupedPbs] = useState({});
    const [openSections, setOpenSections] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        async function fetchAthletes() {
            try {
                const response = await axios.get(`${api_base_url}/v1/athlete?id=${id}`, {
                    headers: { 'x-api-key': api_key },
                });
                const { athlete, pbs } = response.data;
                setAthlete(athlete);
                
                const grouped = groupByStroke(pbs);
                setGroupedPbs(grouped);
                
                // Open all sections by default
                const initialOpen = {};
                Object.keys(grouped).forEach(stroke => {
                    initialOpen[stroke] = true;
                });
                setOpenSections(initialOpen);
            } catch (err) {
                console.log(err);
                setError("Failed to fetch athlete");
            } finally {
                setLoading(false);
            }
        }
        fetchAthletes();
    }, [api_key, id]);
    
    const toggleSection = (stroke) => {
        setOpenSections(prev => ({
            ...prev,
            [stroke]: !prev[stroke]
        }));
    };
    
    if (loading) return (
        <div id="content" className="flex items-center justify-center">
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
        <div id="content" className="flex items-center justify-center">
            <div className="text-red-500 text-xl">{error}</div>
        </div>
    );
    
    const strokeOrder = ['Freestyle', 'Backstroke', 'Breaststroke', 'Butterfly', 'Medley', 'Other'];
    const orderedStrokes = strokeOrder.filter(stroke => groupedPbs[stroke]);
    
    return (
        <div className="flex flex-col h-full w-full overflow-hidden">
            <motion.div
                className="px-4 py-3 md:px-6 md:py-6 border-b-2 border-[#83B1D5] flex-shrink-0"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <h1 className="text-3xl md:text-5xl font-bold text-[#F9CE4E] mb-2">
                    {athlete.first_name} {athlete.last_name}
                </h1>
                <div className="flex flex-wrap gap-3 md:gap-4 text-gray-300 text-sm md:text-base justify-center">
                    <span>Born: {athlete.birth_year}</span>
                    <span>{athlete.gender === 0 ? 'Male' : 'Female'}</span>
                </div>
            </motion.div>
            
            <div className="flex-1 overflow-y-auto px-3 py-3 md:px-6 md:py-6">
                <div className="space-y-3 md:space-y-4 max-w-7xl mx-auto">
                    {orderedStrokes.map((stroke, index) => (
                        <motion.div
                            key={stroke}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <StrokeSection
                                stroke={stroke}
                                pbs={groupedPbs[stroke]}
                                isOpen={openSections[stroke]}
                                onToggle={() => toggleSection(stroke)}
                            />
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default Athlete;
