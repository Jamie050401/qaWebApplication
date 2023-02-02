#!/bin/python3

#################################################################################################
# Program:  Python / SQLite Web Application                                                     #
# Filename: auth.py                                                                             #
# Author:   Jamie Allen                                                                         #
# Course:   BSc Digital Technology and Solutions                                                #
# Module:   Software Engineering and Agile                                                      #
# Version:  1.0                                                                                 #
# Date:     xx/xx/23                                                                            #
#################################################################################################

from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import check_password_hash

from db import session_local
from db.models import User
from web.authentication import current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", user=current_user)

    database = session_local()

    email = request.form.get("email")
    password = request.form.get("password")

    user = database.query(User).filter(User.email == email).first()
    if user:
        if check_password_hash(user.password, password):
            flash("Logged in successfully!", category="success")
            current_user.login(user)
            database.close()
            return redirect(url_for("views.index"))

    # Ensures the user remains on the login screen should a login attempt fail
    current_user.login_failed()

    flash("Incorrect email or password, please try again.", category="failure")

    database.close()

    return redirect(url_for("auth.login"))


@auth.route('/logout')
def logout():
    current_user.logout()
    return redirect(url_for("auth.login"))


@auth.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", user=current_user)

    database = session_local()

    email = request.form.get("email")
    first_name = request.form.get("first_name")
    password = request.form.get("password_first")
    password_conf = request.form.get("password_second")

    # Ensures the user is returned to the registration screen if the validation fails
    current_user.register()

    user = database.query(User).filter(User.email == email).first()
    if user:
        flash("Email already exists!", category="failure")
        database.close()
        return redirect(url_for("views.index"))

    new_user = User(email=email, first_name=first_name, password=password,
                    password_conf=password_conf, role_name="User")

    if new_user.is_valid:
        database.add(new_user)
        database.commit()
        flash("User created!", category="success")
        current_user.login(new_user)
        database.close()
        return redirect(url_for("views.index"))

    database.close()

    return redirect(url_for("auth.register"))

#################################################################################################
# File: auth.py                                                                                 #
#                                                                                               #
# Disclaimer: The following source code is the sole work of the author unless otherwise stated. #
#                                                                                               #
# Copyright (c) Jamie Allen. All Rights Reserved.                                               #
#################################################################################################
