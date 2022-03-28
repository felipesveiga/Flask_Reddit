# Esta página é responsável por lançar o site.
from Flask_Reddit import app
if __name__=='__main__':
    # Setando debug = True fará com que as modificações feitas no decorrer do projeto sejam automaticamente no site!
    app.run(debug = True)