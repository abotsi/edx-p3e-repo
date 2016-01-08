# coding: utf-8
"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import os.path
from random import sample, choice, shuffle, randint

from xblock.core import XBlock
from xblock.fields import Scope, Integer, List, Dict
from xblock.fragment import Fragment

from mako.template import Template


class P3eXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

# Fields global to all students
    dict_questions = Dict(
        default={}, scope=Scope.user_state_summary,
        help="The list of all questions",
    )
    max_id_question = Integer(
        default=-0, scope=Scope.user_state_summary,
        help="The biggest identifier given to a question"
            +"Student question ids are positives.",
    )
    dict_answers_to_evaluate = Dict(
        default={}, scope=Scope.user_state_summary,
        help="The list of answers submited at phase 1",
    )
    max_id_answer = Integer(
        default=0, scope=Scope.user_state_summary,
        help="The biggest identifier given to a answer",
    )
    last_id_saved = Integer(
        default=-0, scope=Scope.user_state_summary,
        help="The biggest identifier of a question submited by the professor"
            +"and saved in the student list."
            +"Professor question ids are negatives.",
    )

# Fields specific to the professor
    studio_data = List(
        default=[], scope=Scope.settings,
        help="The list of (question - answer) submitted by the professor"
            +"that will be copied to dict_questions ASAP."
            +"Not erasable or rewritable, only adding is allowed.",
    )

# Fields specific to one student
    current_phase = Integer(
        default=1, scope=Scope.user_state,
        help="The phase currently running",
    )

    phase1_question_indexes = List(
        default=[], scope=Scope.user_state,
        help="The ids of the 3 questions this student answered in phase 1",
    )
    phase2_question_index = Integer(
        default=0, scope=Scope.user_state,
        help="The id of the question this student asked in phase 2",
    )
    phase3_data = List(
        default=[], scope=Scope.user_state,
        help="The 9 triplets (answer id, question id, clue id) referring to what this student corrected in phase 3",
    )


    def studio_view(self, context=None):
        """This is the view displaying xblock form in studio."""

        print
        print " --> Appel a la studio_view"
        print "     self.studio_data : ", self.studio_data
        print

        if not self.studio_data:
            print "     there are no studio_data"
            print " <-- Fin"
            return self.load_view_studio()


        print "     there are studio_data"
        print " <-- Fin"
        return self.load_view_studio(self.studio_data)

    @XBlock.json_handler
    def validate_studio(self, data, suffix=''):
        """
        A handler to receive a question from the studio
        """
        print
        print " --> Appel au handler studio"
        print "     data : ", data

        # Si les donnees envoyees par le client sont non vides
        if data['q'] and data['r']:

            # On prend le plus grand id et on l'incremente
            data['id'] = 1
            if self.studio_data:
                data['id'] += int(self.studio_data[-1]['id'])

            # On ajoute les donnees
            self.studio_data.append(data)
            print "     self.studio_data : ", self.studio_data
            print " <-- Fin du handler"
            print

            # On renvoie l'id pour mettre a jour l'interface client
            return data['id']


    def student_view(self, context=None):
            # On cree quelques fausses données si besoin
        # if len(self.dict_questions)<5:
        #     t_q = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed condimentum enim vitae tortor rhoncus ?"
        #     t_r = "Phasellus suscipit dui at orci molestie pellentesque. Integer placerat convallis lacus. Integer eleifend, augue non consequat luctus, urna dui mollis."
        #     for i in range(5):
        #         self.add_question(t_q, t_r, p_is_prof=True)
        # if len(self.dict_questions)<10:
        #     t_q = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed condimentum enim vitae tortor rhoncus ?"
        #     t_r = "Phasellus suscipit dui at orci molestie pellentesque. Integer placerat convallis lacus. Integer eleifend, augue non consequat luctus, urna dui mollis."
        #     for i in range(5):
        #         self.add_question(t_q, t_r)
        # if len(self.dict_answers_to_evaluate)<10:
        #     t_s = "Nulla id auctor orci. Vivamus pharetra eu felis vitae iaculis. Sed ornare, velit vitae faucibus sollicitudin, orci nunc mollis ipsum."
        #     for i in range(10):
        #         self.add_answer_to_evaluate(randint(1,10), t_s)

        print
        print " --> Appel a la student_view"
        print "     n° de phase :", self.current_phase


            # On copie les questions profs vers la liste accessible par les etudiants
        # On recupere le plus grand id de la list des questions prof (le dernier ajoute)
        last_id_created = 0
        if self.studio_data:
            last_id_created = self.studio_data[-1]['id']

        print "     last_id_created : ", last_id_created
        print "     self.last_id_saved : ", self.last_id_saved

        if last_id_created > self.last_id_saved:
            # on ajoute dans dict_q les question de l_prof qui on un id plus grand que last_id_dict
            # c a d : en partant de la fin de la liste, on ajoute tout les elem jusqu a last_id_dict
            print "     Le prof a ajoute de nouvelles questions ! "

            # On parcourt la list prof depuis la fin
            for new_q_p in reversed(self.studio_data):
                # et on s'arrete quand on trouve un indice qu'on avait deja enregistre
                if new_q_p['id'] <= self.last_id_saved:
                    break

                # On ajoute la nouvelle question dans le dict
                self.add_studio_question(new_q_p['q'], new_q_p['r'], new_q_p['id'])
                print "     question ajoutee : ", new_q_p['id']

            # Puis on met a jour le dernier id qu'on a enregistre
            self.last_id_saved = last_id_created


        # On charge les donnees necessaires a la phase actuelle
        data = []
        if (self.current_phase == 1):
            data = self.get_data_phase1()
        elif (self.current_phase == 3):
            data = self.get_data_phase3()

        print "     data : ", data
        print " <-- Fin"
        print

        # On affiche une page d'erreur si il n'y a pas suffisament de donnees pour cette phase
        if not data :
            print "     warning : there is not enough data for this phase"
            return self.load_view("error.html")

        return self.load_view("phase"+str(self.current_phase)+".html", data)


    def load_view_studio(self, data=[]):
        """Loading the whole XBlock fragment"""
        frag = Fragment(self.render_template("studio.html", data))
        frag.add_css(self.resource_string("static/css/p3exblock.css"))
        frag.add_css(self.resource_string("static/css/p3exblock_studio.css"))
        frag.add_javascript(self.resource_string("static/js/src/p3exblock_studio.js"))
        frag.initialize_js('P3eXBlock')
        return frag

    def load_view(self, filename, data=[]):
        """Loading the whole XBlock fragment"""
        frag = Fragment(self.render_template(filename, data))
        frag.add_css(self.resource_string("static/css/p3exblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/p3exblock.js"))
        frag.initialize_js('P3eXBlock')
        return frag

    def render_template(self, filename, data=[]):
        """Handy helper for loading mako template."""
        f = os.path.dirname(__file__) +"/templates/"+ filename
        html = Template(filename=f, input_encoding='utf-8').render(data=data)
        return html

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def get_data_phase1(self, context=None):
        """
        Selecting 3 random questions for the first phase
        """

        # S'il n'en a pas encore, on selectionne des questions pour l'etudiant
        if not self.phase1_question_indexes:
            print "     start picking questions for phase 1"

            # On verifie s'il y a assez de question a poser
            if len(self.dict_questions)<3:
                print "     there is less than 3 questions"
                return None

            # si il n'y a pas encore de questions type `etudiant`
            if len(self.get_student_questions() ) == 0:
                # on prend 3 questions profs
                self.phase1_question_indexes = sample(self.get_prof_questions(), 3)
            else:
                # on prend au hasard des indexes de questions profs
                self.phase1_question_indexes = sample(self.get_prof_questions(), 2)
                # puis on ajoute une question etudiant
                self.phase1_question_indexes.append(sample(self.get_student_questions(), 1)[0]) # [0] --> pour acceder a l'unique element du singleton

            #on melange les questions pour que celle de l'etudiant ne soit pas toujours a la fin
            shuffle(self.phase1_question_indexes)

            print
            print "     Phase 1, selected questions : ", self.phase1_question_indexes
            print

        lst_txt = []
        for i in self.phase1_question_indexes:
            # on prend le texte des questions
            lst_txt.append(self.dict_questions[i]['s_text'])

        return lst_txt


    def get_data_phase3(self, context=None):
        """
        The third phase of the P3E, extracting 9 questions and answers
        """

        # Si on a pas encore tire les reponses
        if not self.phase3_data:
            print "     start picking answers to evaluate for phase 3"

            # On recupere toutes les reponses non evaluees
            dict_unevaluated_answers = self.get_unevaluated_answers()

            # ...on enleve les reponses de l'utilisateur courrant
            # /!\wrong/!\ -> d...s = [elt for elt in d...s if elt not in self.phase1_question_indexes]
            dict_unevaluated_answers = [elt for elt in dict_unevaluated_answers ]

            # On verifie s'il y a assez de reponse a evaluer
            if len(dict_unevaluated_answers) < 9:
                print "     there is less than 9 answers to evaluate"
                return None

            # ...puis on en prend 9 parmi celles-ci
            for answer_id in sample(dict_unevaluated_answers, 9):
                # et on selectionne le meilleur corrige pour chacune
                question_id = self.dict_answers_to_evaluate[answer_id]['n_question_id']
                clue_id = self.get_best_clue_index(question_id)
                self.phase3_data.append( {'answer_id':answer_id, 'question_id':question_id, 'clue_id':clue_id} )


            print
            print "     Phase 3, selected answers : ", self.phase3_data
            print

        data = []
        for e in self.phase3_data:
            # On prend le texte de chaque reponse,
            answer_text = self.dict_answers_to_evaluate[e['answer_id']]['s_text']
            # ...l'enonce de la question correspondante,
            question_text = self.dict_questions[e['question_id']]['s_text']
            # ...ainsi que le texte du meilleur corrige,
            clue_text = self.dict_questions[e['question_id']]['lst_clue_answer'][e['clue_id']]['s_text']

            data.append({'text':question_text, 'clue_answer':clue_text, 'answer_to_evaluate':answer_text})

        return data

    @XBlock.json_handler
    def validate_phase1(self, data, suffix=''):
        """
        A handler to validate the phase 1
        """
        print
        print " --> Appel au handler 1"
        print "     data : ", data

        for i in range(3):
            question_index = self.phase1_question_indexes[i]
            answer = data[i]['answer']
            grade = int(data[i]['question_grade'])

            # Pour ne pas perdre de precision a cause de la moyenne,
            # on sauvegarde separement le total de evaluations et le nombre d'evaluation
            self.dict_questions[question_index]['nb_of_grade']+=1
            self.dict_questions[question_index]['n_grade'] += grade
            self.add_answer_to_evaluate(question_index, answer)

        self.current_phase = 2
        print " <-- Fin du handler"

        return self.render_template("phase2.html")

    @XBlock.json_handler
    def validate_phase2(self, data, suffix=''):
        """
        A handler to validate the phase 2
        """

        print
        print " --> Appel au handler 2"
        print "     data['question'] : ", data['question']
        print "     data['answer'] : ", data['answer']

        self.add_question(data['question'], data['answer'])
        self.phase2_question_index = self.max_id_question
        print "     self.phase2_question_index : ", self.phase2_question_index
        print

        data = self.get_data_phase3()
        # data_for_phase3 = []
        self.current_phase = 3

        # On affiche une page d'erreur si il n'y a pas suffisament de donnees pour cette phase
        if not data :
            print "     warning : there is not enough data for this phase"
            return self.render_template("error.html")

        print " <-- Fin du handler"

        return self.render_template("phase3.html", data)

    @XBlock.json_handler
    def validate_phase3(self, data, suffix=''):
        """
        A handler to validate the phase 3
        """

        print " --> Appel au handler 3"
        print "     data['answer_grades'] : ", data['answer_grades']
        print "     data['clue_grades'] : ", data['clue_grades']
        print "     data['new_solutions'] : ", data['new_solutions']
        print

        for i in range(9):
            answer_id = self.phase3_data[i]['answer_id']
            question_id = self.phase3_data[i]['question_id']
            clue_id = self.phase3_data[i]['clue_id']

            # on ajoute une note a la reponse
            self.dict_answers_to_evaluate[answer_id]['n_grade'] += int(data['answer_grades'][i])
            self.dict_answers_to_evaluate[answer_id]['nb_of_grade'] += 1

            # on ajoute une note au corrige
            self.dict_questions[question_id]['lst_clue_answer'][clue_id]['n_grade'] += int(data['clue_grades'][i])
            self.dict_questions[question_id]['lst_clue_answer'][clue_id]['nb_of_grade'] += 1

            # le cas echeant, on enregistre la nouvelle solution proposee par le correcteur
            if data['new_solutions'][i]:
                self.add_solution(question_id, data['new_solutions'][i])

        self.current_phase = 4
        print " <-- Fin du handler"

        return self.render_template("phase4.html")


    def add_question(self, p_question_txt, p_answer_txt, p_is_prof=False):
        self.max_id_question+=1
        res = {
            'n_writer_id': -1,
            'is_prof': p_is_prof,
            's_text': p_question_txt,
            'lst_clue_answer': [{
                'n_writer_id': -1,
                's_text': p_answer_txt,
                'n_grade': 5,
                'nb_of_grade': 1,
            }],
            'n_grade': 0,
            'nb_of_grade': 0,
        }
        # la cle d'un field.Dict passe au format unicode lorsque edX l'enregistre
        self.dict_questions[unicode(self.max_id_question)] = res

    def add_studio_question(self, p_question_txt, p_answer_txt, p_id):
        res = {
            'n_writer_id': -1,
            'is_prof': True,
            's_text': p_question_txt,
            'lst_clue_answer': [{
                'n_writer_id': -1,
                's_text': p_answer_txt,
                'n_grade': 5,
                'nb_of_grade': 1,
            }],
            'n_grade': 0,
            'nb_of_grade': 0,
        }
        # la cle d'un field.Dict passe au format unicode lorsque edX l'enregistre
        # on enregistre l'id des questions profs en negatif
        self.dict_questions[unicode(0 - p_id)] = res

    def add_answer_to_evaluate(self, id_question, p_s_text):
        self.max_id_answer+=1
        res = {
            'n_question_id': unicode(id_question),
            'n_writer_id': -1,
            's_text': p_s_text,
            'n_grade': 0,
            'nb_of_grade': 0,
        }
        self.dict_answers_to_evaluate[unicode(self.max_id_answer)] = res

    def add_solution(self, id_question, p_s_text):
        res = {
            'n_writer_id': -1,
            's_text': p_s_text,
            'n_grade': 5,
            'nb_of_grade': 1,
        }
        self.dict_questions[id_question]['lst_clue_answer'].append(res)


    def get_prof_questions(self):
        """Return a subset of all questions written by a professor"""
        return dict(filter(lambda k: k[1]['is_prof']==True, self.dict_questions.items()))

    def get_student_questions(self):
        """Return the subset of questions written by students"""
        return dict(filter(lambda k: k[1]['is_prof']==False, self.dict_questions.items()))

    def get_unevaluated_answers(self):
        """Return the subset of questions written by students"""
        return dict(filter(lambda k: k[1]['nb_of_grade']<3, self.dict_answers_to_evaluate.items()))

    def get_best_clue_index(self, question_id):
        """Return the best clue answer for a question"""
        max_i = max_v = 0
        for i, v in enumerate(self.dict_questions[question_id]['lst_clue_answer']):
            # calcule la note moyenne en gerant le cas 0
            m = (v['n_grade']/v['nb_of_grade'])|0
            if m > max_v:
                max_i, max_v = i, m

        return max_i


    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("P3eXBlock",
             """<p3exblock/>
             """),
        ]



        # q = "Que permet de faire le théorème de Bayes ? Donner un exemple ?"
        # r = "Il permet d'inverser des probabilités pourvu qu'on ait des connaissances préalables."
        # r_etu = "Si l'on connait P(A), P(B) et P(A|B),le théorème de Bayes nous permet de calculer P(B|A)."
        # for i in range(5):
        #     self.add_studio_question(q, r)
