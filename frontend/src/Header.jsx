import { useNavigate } from 'react-router-dom';

export default function Header() {
    const navigate = useNavigate();

    return (
        <header onClick={() => navigate("/")}>
            <div
                id="header-wrapper"
                tabIndex={0}
                className="grid justify-center items-center"
            >
                <img 
                    id="header-logo" 
                    draggable="false"
                    src="/img/header-logo-v3.png" 
                    alt="SCWR Logo" 
                />
            </div>
        </header>
    );
}
