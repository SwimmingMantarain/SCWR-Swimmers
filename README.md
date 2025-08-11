# 🏊‍♂️ SCWR Swimmers

A web app for viewing useful info about the **Swimming Club Wauterbos Rhode**.

## ✨ Current Features
- ⚡ **FastAPI-powered REST API**
- 🗄 **SQLite** database for persistence
- 🖥 **Sleek, easy-to-use admin panel**
- 🐧 Cool (definitely not data-collecting 😉) server script

## 📦 Installation
```bash
git clone https://github.com/SwimmingMantarain/SCWR-Swimmers.git --depth 1
cd SCWR-Swimmers
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Running the App
```bash
./run_server.sh
```

App will be available at:
- 🌐 [http://localhost:8000](http://localhost:8000)
- 🖧 `http://192.168.x.xxx:8000` (for LAN access)

## 📡 API Endpoints (`/v1` current)
| Method | Endpoint           | Description                                      |
|--------|--------------------|--------------------------------------------------|
| POST   | `/v1/add-swimmer`  | ➕ Add a swimmer to the database                 |
| POST   | `/v1/remove-swimmer` | ➖ Remove a swimmer from the database          |
| POST   | `/v1/sync-swimmers` | 🔄 Sync current swimmers from [https://swimrankings.net](https://swimrankings.net) |

To see all endpoints:
1. Launch the app with:
   ```bash
   ./run_server.sh
   ```
2. Visit the interactive docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🛠 Development
- 🐍 Python 3.12+
- 🚀 FastAPI\[standard]
- 🗃 SQLAlchemy
- 🔐 bcrypt (admin password hashing)
- ⚙️ python-dotenv

## 🗓 Planned Features
- 🏆 Viewing club records
- ⏱️ Viewing athlete PBs
- 📊 Viewing meet results (past, present, upcoming)
- 📺 Viewing meet livestreams

## 📜 License
This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
