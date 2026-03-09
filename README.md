1. on root folder run
 ```bash
 .\myenv\Scripts\activate
 ```
2. on root folder do uvicorn backend.main:app --host 0.0.0.0 --port 5000 --reload
 ```bash
 uvicorn backend.main:app --host 0.0.0.0 --port 5000 --reload
 ```
3. on frontend folder do npm run dev
 ```bash
 npm run dev
 ```
 4. open http://localhost:5173/ in browser
 