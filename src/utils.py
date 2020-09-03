from flask import jsonify, url_for

class APIException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

def generate_sitemap(app):
    links = ['/admin/']
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            if "/admin/" not in url:
                links.append(url)

    links_html = "".join(["<li><a href='" + y + "'>" + y + "</a></li>" for y in links])
    return """
        <div style="text-align: center;">
        <img style="max-height: 80px" src='https://ucarecdn.com/3a0e7d8b-25f3-4e2f-add2-016064b04075/rigobaby.jpg' />
        <h1>Rigo welcomes you to your API!!</h1>
        <p>API HOST: <script>document.write('<input style="padding: 5px; width: 300px" type="text" value="'+window.location.href+'" />');</script></p>
        <p>Start working on your proyect by following the <a href="https://github.com/4GeeksAcademy/flask-rest-hello/blob/master/docs/_QUICK_START.md" target="_blank">Quick Start</a></p>
        <p>Remember to specify a real endpoint path like: </p>
        <ul style="text-align: left;">"""+links_html+"</ul></div>"

def add_user_authentification(user_info):
    print(user_info)
    username_validation = check_username(user_info)
    email_validation = check_email(user_info)
    password_validation = check_password(user_info)

    if username_validation == True and email_validation == True and password_validation == True:
        return True
    else: 
        return False
    

def check_username(user_info):
    username = user_info.get('username')
    if len(username) > 5:
        if username != "":
            return True
    else:
        return False, "Username can't be empty"

def check_password(user_info):
    password = user_info.get('password')
    check_upper_case = password.isupper()
    check_lower_case = password.islower()
    check_alphanum = password.isalnum()
    check_length = len(password)
    check_spaces = False
    check_numbers = False

    for char in password:
        if char.isspace() == True:
            check_spaces = True
        if char.isdigit() == True:
            check_numbers = True

    if check_upper_case == False and check_lower_case == False and check_alphanum == False and check_length >= 8 and check_spaces == False and check_numbers == True:
        return True
        print("upper: ", check_upper_case, " lower: ", check_lower_case, " alnum: ", check_alphanum, " length: ", check_length, " spaces: ", check_spaces, " numbers: ", check_numbers )
    else:
        return False
        print("upper: ", check_upper_case, " lower: ", check_lower_case, " alnum: ", check_alphanum, " length: ", check_length, " spaces: ", check_spaces, " numbers: ", check_numbers )

    

    
    # password = user_info.get('password')
    # password_lower = password.islower()
    # password_upper = password.isupper()
    # if len(password) > 8 and password_lower == False and password_upper == False:
    #     return True
    # else:
    #     return False

def check_email(user_info):
    email = user_info.get('email')
    if "@" in email:
        return True
    else:
        return False
        
