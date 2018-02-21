
# TEST motherfucker
class Employe(object):
    id = {'name': 'id', 'index': True}
    name = {'name': 'name', 'index': False}
    surname = {'name': 'surname', 'index': False}
    job_title = {'name': 'job_title', 'index': False}
    pseudo = {'name': 'pseudo', 'index': False}
    password = {'name': 'password', 'index': False}

    def __init__(self, id, name, surname, job_title, pseudo, password):
        self.id = id
        self.name = name
        self.surname = surname
        self.job_title = job_title
        self.pseudo = pseudo
        self.password = password
