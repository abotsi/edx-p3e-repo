# coding: utf-8
"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import os.path
from random import sample, choice, shuffle, randint
from time import time
import logging
logger = logging.getLogger('p3exblock')
logger.setLevel(logging.DEBUG)

logging.getLogger('django').setLevel(logging.WARNING)

formatter = logging.Formatter('\n[%(asctime)s] %(message)s')

file_handler = logging.FileHandler("/var/log/p3exblock.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List, Dict
from xblock.fragment import Fragment

from mako.template import Template


class P3eXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    current_phase = Integer(
        default=1, scope=Scope.user_state,
        help="The phase currently running",
    )

    t_stud_last_modif = Integer(
        default=0, scope=Scope.user_state,
        help="Date of the last modification made by a student",
    )
    t_prof_last_modif = Integer(
        default=0, scope=Scope.settings,
        help="Date of the last modification made by the professor",
    )

    dict_studio_questions = Dict(
        default={}, scope=Scope.settings,
        help="The list of questions set up by the professor",
    )
    max_id_studio_question = Integer(
        default=0, scope=Scope.settings,
        help="The biggest identifier of a question submited by the professor",
    )
    var_test = Integer(
        default=0, scope=Scope.content,
    )

    dict_questions = Dict(
        default={}, scope=Scope.user_state_summary,
        help="The list of all questions",
    )
    max_id_question = Integer(
        default=0, scope=Scope.user_state_summary,
        help="The biggest identifier given to a question",
    )
    dict_answers_to_evaluate = Dict(
        default={}, scope=Scope.user_state_summary,
        help="The list of answers submited at phase 1",
    )
    max_id_answer = Integer(
        default=0, scope=Scope.user_state_summary,
        help="The biggest identifier given to a answer",
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

        logger.debug("On entre dans la partie prof")
        logger.debug("self.max_id_question : %s", self.max_id_question)
        logger.debug("self.dict_questions : %s", self.dict_questions)
        logger.debug("self.max_id_studio_question : %s", self.max_id_studio_question)
        logger.debug("self.dict_studio_questions : %s", self.dict_studio_questions)
        logger.debug("self.var_test : %s", self.var_test)

        q = "Que permet de faire le théorème de Bayes ? Donner un exemple ?"
        r = "Il permet d'inverser des probabilités pourvu qu'on ait des connaissances préalables."
        # r_etu = "Si l'on connait P(A), P(B) et P(A|B),le théorème de Bayes nous permet de calculer P(B|A)."
        for i in range(5):
            self.add_studio_question(q, r)

        try:
            self.var_test += 18
        except Exception, e:
            logger.error("Voici l'erreur : %s", e)
        logger.debug("self.var_test : %s", self.var_test)

        logger.debug("self.max_id_question : %s", self.max_id_question)
        logger.debug("self.dict_questions : %s", self.dict_questions)
        logger.debug("self.max_id_studio_question : %s", self.max_id_studio_question)
        logger.debug("self.dict_studio_questions : %s", self.dict_studio_questions)
        logger.debug("On sort de la partie prof")

        self.t_prof_last_modif = time()
        return Fragment(self.resource_string("templates/studio.html"))

    def student_view(self, context=None):
        logger.debug("On entre dans la partie etudiant")
        logger.debug("self.max_id_question : %s", self.max_id_question)
        logger.debug("self.dict_questions : %s", self.dict_questions)
        logger.debug("self.max_id_studio_question : %s", self.max_id_studio_question)
        logger.debug("self.dict_studio_questions : %s", self.dict_studio_questions)
        logger.debug("self.var_test : %s", self.var_test)
        # On copie les données entrees par prof
        if self.t_prof_last_modif>self.t_stud_last_modif:
            self.dict_questions = self.dict_studio_questions
            self.max_id_question = self.max_id_studio_question
            self.t_stud_last_modif = self.t_prof_last_modif

        # On cree quelques fausses données si besoin
        if len(self.dict_questions)<5:
            logger.debug("Creation de fausses questions prof")
            t_q = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed condimentum enim vitae tortor rhoncus ?"
            t_r = "Phasellus suscipit dui at orci molestie pellentesque. Integer placerat convallis lacus. Integer eleifend, augue non consequat luctus, urna dui mollis."
            for i in range(5):
                self.add_question(t_q, t_r, p_is_prof=True)
        if len(self.dict_questions)<10:
            logger.debug("Creation de questions etudiant")
            t_q = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed condimentum enim vitae tortor rhoncus ?"
            t_r = "Phasellus suscipit dui at orci molestie pellentesque. Integer placerat convallis lacus. Integer eleifend, augue non consequat luctus, urna dui mollis."
            for i in range(5):
                self.add_question(t_q, t_r)
        if len(self.dict_answers_to_evaluate)<10:
            t_s = "Nulla id auctor orci. Vivamus pharetra eu felis vitae iaculis. Sed ornare, velit vitae faucibus sollicitudin, orci nunc mollis ipsum."
            for i in range(10):
                self.add_answer_to_evaluate(randint(1,10), t_s)

        data = []
        if (self.current_phase == 1):
            data = self.get_data_phase1()
        elif (self.current_phase == 3):
            data = self.get_data_phase3()

        logger.debug("self.var_test : %s", self.var_test)
        logger.debug("self.max_id_question : %s", self.max_id_question)
        logger.debug("self.dict_questions : %s", self.dict_questions)
        logger.debug("self.max_id_studio_question : %s", self.max_id_studio_question)
        logger.debug("self.dict_studio_questions : %s", self.dict_studio_questions)
        logger.debug("On sort de la partie etudiant")

        return self.load_current_phase(data)


    def load_current_phase(self, p_data):
        """Loading the whole XBlock fragment"""

        frag = Fragment(self.get_current_html(p_data))
        frag.add_css(self.resource_string("static/css/p3exblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/p3exblock.js"))
        frag.initialize_js('P3eXBlock')
        return frag

    def get_current_html(self, p_data=[]):
        """Handy helper for loading mako template."""
        f = os.path.dirname(__file__) +"/templates/phase"+ str(self.current_phase) +".html"
        html = Template(filename=f, input_encoding='utf-8').render(data=p_data)
        return html

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def get_data_phase1(self, context=None):
        """
        Selecting 3 random questions for the first phase
        """
        
        if not self.phase1_question_indexes:
            # on prend au hasard des indexes de questions profs
            self.phase1_question_indexes = sample(self.get_prof_questions(), 2)
            # puis on ajoute une question etudiant
            self.phase1_question_indexes.append(sample(self.get_student_questions(), 1)[0]) # [0] --> pour acceder a l'unique element du singleton
            #on melange les questions pour que celle de l'etudiant ne soit pas toujours a la fin
            shuffle(self.phase1_question_indexes)

            print
            print "--> Phase 1, selected questions : ", self.phase1_question_indexes
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
            # On recupere toutes les reponses non evaluees
            dict_unevaluated_answers = self.get_unevaluated_answers()

            # ...on enleve les reponses de l'utilisateur courrant
            # wrong -> d...s = [elt for elt in d...s if elt not in self.phase1_question_indexes]
            dict_unevaluated_answers = [elt for elt in dict_unevaluated_answers ]

            # ...puis on en prend 9 parmi celles-ci
            for answer_id in sample(dict_unevaluated_answers, 9):
                # et on selectionne le meilleur corrige pour chacune
                question_id = self.dict_answers_to_evaluate[answer_id]['n_question_id']
                clue_id = self.get_best_clue_index(question_id)
                self.phase3_data.append( {'answer_id':answer_id, 'question_id':question_id, 'clue_id':clue_id} )


            print
            print "--> Phase 3, selected answers : ", self.phase3_data
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

        return self.get_current_html()

    @XBlock.json_handler
    def validate_phase2(self, data, suffix=''):
        """
        A handler to validate the phase 2
        """

        print
        print " --> Appel au handler 2"
        print
        print "     data['question'] : ", data['question']
        print "     data['answer'] : ", data['answer']
        print

        self.add_question(data['question'], data['answer'])
        self.phase2_question_index = self.max_id_question

        data_for_phase3 = self.get_data_phase3()

        self.current_phase = 3

        print " <-- Fin du handler"

        return self.get_current_html(data_for_phase3)

    @XBlock.json_handler
    def validate_phase3(self, data, suffix=''):
        """
        A handler to validate the phase 3
        """

        print " --> Appel au handler 3"
        print
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

        return self.get_current_html()

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
        # la cle d'un field.Dict passe au format unicode
        self.dict_questions[unicode(self.max_id_question)] = res

    def add_studio_question(self, p_question_txt, p_answer_txt):
        self.max_id_studio_question+=1
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
        # la cle d'un field.Dict passe au format unicode
        self.dict_studio_questions[unicode(self.max_id_studio_question)] = res

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
