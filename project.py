from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, CatalogItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

# Connect to Database and create database session
engine = create_engine(
    'sqlite:///catalogproject.db',
    connect_args={
        'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    """
    Renders login screen
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
    Gathers data from Facebook Sign In API and places it
    inside a session variable.
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type=fb_' +
           'exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'
           % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange
        we have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and
        replace the remaining quotes with nothing so that it can be used
        directly in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = ("https://graph.facebook.com/v2.8/me?access_token=%s&fields=" +
           "name,id,email" % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = ("https://graph.facebook.com/v2.8/me/picture?access_token=%s&" +
           "redirect=0&height=200&width=200" % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += 'style="width: 300px; height: 300px;border-radius: 150px;"'
    output += '"-webkit-border-radius: 150px;-moz-border-radius: 150px;">'

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """
    Ends a facebook's user session
    """
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Gathers data from Google Sign In API and places it
    inside a session variable.
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += 'style="width: 300px; height: 300px;border-radius: 150px;"'
    output += '"-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    """
    Create a new user in the case of record in the DB
    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    Retrieve user object from DB using an ID
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """
    Retrieve user's ID from DB using an e-mail
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    """
    Close an user session login
    """
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Catalog Information


@app.route('/catalog/<int:catalog_id>/items/JSON')
def restaurantMenuJSON(catalog_id):
    """
    JSON API interface to retrieve an items' catalogs list
    """
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(CatalogItem).filter_by(
        catalog_id=catalog_id).all()
    return jsonify(CatalogItems=[i.serialize for i in items])


@app.route('/catalog/<int:catalog_id>/items/<int:item_id>/JSON')
def menuItemJSON(catalog_id, item_id):
    """
    JSON API interface to retrieve data values of catalogs' item
    """
    catalogItem = session.query(CatalogItem).filter_by(id=item_id).one()
    return jsonify(catalogItem=catalogItem.serialize)


@app.route('/catalog/JSON')
def catalogsJSON():
    """
    JSON API interface to retrieve a list of catalogs
    """
    catalogs = session.query(Catalog).all()
    return jsonify(catalogs=[c.serialize for c in catalogs])


# Show all Catalogs


@app.route('/')
@app.route('/catalog/')
def showCatalogs():
    """
    Function to return and render a catalogs list
    """
    catalogs = session.query(Catalog).order_by(asc(Catalog.name))
    if 'username' not in login_session:
        return render_template('publiccatalog.html', catalogs=catalogs)
    else:
        return render_template('catalog.html', catalogs=catalogs)


@app.route('/catalog/<int:catalog_id>/')
@app.route('/catalog/<int:catalog_id>/item/')
def showItem(catalog_id):
    """
    Function to return and render a catalogs' items list
    """
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    creator = getUserInfo(catalog.user_id)
    items = session.query(CatalogItem).filter_by(
        catalog_id=catalog_id).all()
    if ('username' not in login_session or
       creator.id != login_session['user_id']):
        return render_template(
            'publicmenu.html',
            items=items,
            catalog=catalog,
            creator=creator)
    else:
        return render_template(
            'menu.html',
            items=items,
            catalog=catalog,
            creator=creator)


# Create a new catalog

@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    """
    Function to render a new catalogs' page and store it
    case performed
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCatalog = Catalog(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCatalog)
        flash('New Catalog %s Successfully Created' % newCatalog.name)
        session.commit()
        return redirect(url_for('showCatalogs'))
    else:
        return render_template('newcatalog.html')

# Edit a restaurant


@app.route('/catalog/<int:catalog_id>/edit/', methods=['GET', 'POST'])
def editCatalog(catalog_id):
    """
    Function to render a catalogs' edit page and store
    the changes case performed
    """
    editedCatalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCatalog.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You're not authorized" +
                "to edit this restaurant. Please create your own restaurantr" +
                " in ordeto edit.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        if request.form['name']:
            editedCatalog.name = request.form['name']
            flash('Catalog Successfully Edited %s' % editedCatalog.name)
            return redirect(url_for('showCatalogs'))
    else:
        return render_template('editCatalog.html', catalog=editedCatalog)


# Delete a catalog

@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    """
    Function to render a catalogs' delete page and remove
    the record from DB case performed
    """
    catalogToDelete = session.query(
        Catalog).filter_by(id=catalog_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if catalogToDelete.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You're not authorized" +
                " to delete this restaurant. Please create your own" +
                " restaurant in order to delete.');}" +
                "</script><body onload='myFunction()'>")
    if request.method == 'POST':
        session.delete(catalogToDelete)
        flash('%s Successfully Deleted' % catalogToDelete.name)
        session.commit()
        return redirect(url_for('showCatalogs', catalog_id=catalog_id))
    else:
        return render_template('deleteCatalog.html', catalog=catalogToDelete)

# Create a new menu item


@app.route('/catalog/<int:catalog_id>/item/new/', methods=['GET', 'POST'])
def newCatalogItem(catalog_id):
    """
    Function to render a new catalogs' item page and store it
    case performed
    """
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if login_session['user_id'] != catalog.user_id:
        return ("<script>function myFunction() {alert('You're not authorized" +
                " to add menu items to this restaurant. Please create your " +
                " own restaurant in order to add items.');}" +
                "</script><body onload='myFunction()'>")
    if request.method == 'POST':
        newItem = CatalogItem(
            name=request.form['name'],
            description=request.form['description'],
            catalog_id=catalog_id,
            user_id=catalog.user_id)
        session.add(newItem)
        session.commit()
        flash('New Catalogs %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showItem', catalog_id=catalog_id))
    else:
        return render_template('newcatalogitem.html', catalog_id=catalog_id)

# Edit a item from catalog


@app.route(
    '/catalog/<int:catalog_id>/item/<int:item_id>/edit',
    methods=[
        'GET',
        'POST'])
def editMenuItem(catalog_id, item_id):
    """
    Function to render an edit page of catalogs'
    item and update it case performed
    """
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CatalogItem).filter_by(id=item_id).one()
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if login_session['user_id'] != catalog.user_id:
        return ("<script>function myFunction() {alert('You're not authorized" +
                " to edit menu items to this catalog. Please create your " +
                " own catalog in order to edit items.');}" +
                "</script><body onload='myFunction()'>")
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("Catalog's Item Successfully Edited")
        return redirect(url_for('showItem', catalog_id=catalog_id))
    else:
        return render_template(
            'editcatalogitem.html',
            catalog_id=catalog_id,
            item_id=item_id,
            item=editedItem)


# Delete a catalog item


@app.route(
    '/catalog/<int:catalog_id>/item/<int:item_id>/delete',
    methods=[
        'GET',
        'POST'])
def deleteCatalogItem(catalog_id, item_id):
    """
    Function to render an delete page of catalogs'
    item and remove it case performed
    """
    if 'username' not in login_session:
        return redirect('/login')
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    itemToDelete = session.query(CatalogItem).filter_by(id=item_id).one()
    if login_session['user_id'] != catalog.user_id:
        return ("<script>function myFunction() {alert('You're not authorized" +
                " to delete catalog's items to this Catalog. Please create" +
                " your own Catalog in order to delete items.');}" +
                "</script><body onload='myFunction()'>")
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Catalog's Item Successfully Deleted")
        return redirect(url_for('showCatalogs', catalog_id=catalog_id))
    else:
        return render_template('deleteCatalogItem.html', item=itemToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    """
    The root function to close open session independent
    of oauth provider
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalogs'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalogs'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
