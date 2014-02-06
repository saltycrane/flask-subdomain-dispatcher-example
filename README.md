This demonstrates how to run a local development server which uses a
different configuration based on the subdomain of the request. It
creates a separate instance of the app per subdomain. See here for more
information:
<http://flask.pocoo.org/docs/patterns/appdispatch/#dispatch-by-subdomain>


1. Add the following to your hosts file (/etc/hosts on Ubuntu):

        0.0.0.0 dev.localhost
        0.0.0.0 qa.localhost

2. Install Flask

        virtualenv venv
        source venv/bin/activate
        pip install Flask==0.10.1

3. Run the local development server

        python subdomainexample.py

4. Visit the following URLs in the browser:
   - <http://localhost:5000/>
   - <http://dev.localhost:5000/>
   - <http://qa.localhost:5000/>
