#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, request, url_for, redirect

app = Flask(__name__)


@app.route('/')
def accueil():
    mots = ["bonjour", "à", "toi,", "visiteur."]
    puces = ''.join("<li>{}</li>".format(m) for m in mots)
    return """<!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8" />
                <title>{titre}</title>
            </head>

            <body>
                <h1>{titre}</h1>
                <ul>
                    {puces}
                </ul>
            </body>
        </html>""".format(titre="Bienvenue !", puces=puces)


@app.route('/la')
def ici():
    return "Le chemin de 'ici' est : " + request.path


@app.route('/google')
def redirection_google():
    return redirect(url_for('ici'))


if __name__ == '__main__':
    app.run(debug=True)
