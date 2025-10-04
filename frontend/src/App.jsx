import './App.css'
import './Mobile.css'

// My shtuff
import Header from "./Header"

function random(length) {
    return Math.floor(Math.random() * length) + 1;
}

function App() {
    return (
        <>
            <Header />
            <div id="content">
                <div class="photo-card">
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
                        <span id="card-label">Club Records</span>
                    </div>
                    <img
                        class="photo-card-img"
			draggable="false"
                        src={`/img/records-${random(6)}.jpg`}
                        alt="Club Records Image"></img>
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
        </>
    )
}

export default App
