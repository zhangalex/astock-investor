from app import app

if __name__ == '__main__':
    #app.config['DEBUG'] = True

    app.run(host='0.0.0.0', port=9001, debug=True)
    #app.run(debug=True)

    #in prd: gunicorn -w 4 -b 127.0.0.1:8181 run:app -D --pid ./pid --access-logfile ./app.log --log-level info
    #migration:
    #FLASK_APP=./app/__init__.py flask db init
    #FLASK_APP=./app/__init__.py flask db migrate
    #FLASK_APP=./app/__init__.py flask db upgrade

    #run celery
    #celery -A app.celery worker -B --loglevel=info --pidfile=path
    #adduser --system --group --no-create-home celery
    #chown celery:celery /var/opt/projects/celery
    #systemctl {start|stop|restart|status} celery.service
    # systemctl daemon-reload
    #run monitor
    #nohup flower -A app.celery --address=0.0.0.0 --port=7600 --basic_auth=raymond:start888 > /var/opt/projects/celery/flower.log 2>&1 &
    #http://47.74.134.89:7600/dashboard
