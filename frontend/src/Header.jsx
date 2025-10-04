import * as React from "react";

export default function Header() {
    return (
        <header>
            <div
                id="header-wrapper"
                tabIndex={0}
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
