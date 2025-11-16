from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "MontajMarket Backend Çalışıyor 🚀"}

@app.get("/test")
def test_endpoint():
    return {"status": "OK", "info": "API başarılı şekilde yayında!"}

