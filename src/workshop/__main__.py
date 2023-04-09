import uvicorn
from .settings import options
#from workshop.database import create_db


if __name__=='__main__':
    
    #create_db()
    
    uvicorn.run(
        'workshop.app:app',
        host=options.server_host,
        port=options.server_port,
        reload=True
        )