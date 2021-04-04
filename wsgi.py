from application import create_app
# from OpenSSL import SSL

app = create_app()

if __name__ == '__main__':
    
    app.run(
        host        = '0.0.0.0',
        port        = 443,
        ssl_context =('./application//static//ssl//cert.pem', './application//static//ssl/key.pem'),
        use_reloader=False
    )