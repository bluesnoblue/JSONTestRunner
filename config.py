class Config:
    BOOTSTRAP_SERVE_LOCAL = True  # 启用本地静态文件
    MONGO_URI = 'mongodb://admin:123@mongo:27017/reportserver'

db.createUser({user:"admin",pwd:"123",roles:[{role:"readWrite",db:"reportserver"}]})