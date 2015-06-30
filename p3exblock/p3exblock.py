# coding: utf-8
"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import os.path
from random import sample, choice, shuffle, randint

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
        default=[], scope=Scope.user_state,
        help="The id of the question this student asked in phase 2",
    )
    phase3_answer_indexes = List(
        default=[], scope=Scope.user_state,
        help="The ids of the 9 answers this student corrected in phase 3",
    )
    
    def studio_view(self, context):
        pass

    def student_view(self, context=None):
        if len(self.dict_questions)<5:
            for i in range(5):
                self.add_question("question bidon n"+str(i), "reponse bidon n"+str(i), p_is_prof=True)
                self.add_question("question eleve bidon n"+str(i), "reponse bidon n"+str(i))
            for i in range(20):
                self.add_answer_to_evaluate(randint(1,10), "reponse caca n°"+str(i))

        data = []
        if (self.current_phase == 1):
            data = self.get_data_phase1()
        elif (self.current_phase == 3):
            data = self.get_data_phase3()

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
            # puis on ajoute une question étudiant
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
        if not self.phase3_answer_indexes:
            # On recupere toutes les reponses non evaluees
            dict_unevaluated_answers = self.get_unevaluated_answers()
            # ...on enleve les reponses de l'utilisateur courrant
            dict_unevaluated_answers = [elt for elt in dict_unevaluated_answers if elt not in self.phase1_question_indexes]
            # ...puis on en prend 3 parmi celles-ci
            self.phase3_answer_indexes = sample(dict_unevaluated_answers, 9)

            print
            print "--> Phase 3, selected answers : ", self.phase3_answer_indexes
            print

        data = []
        for i in self.phase3_answer_indexes:
            # On prend le texte de chaque reponses
            answer_text = self.dict_answers_to_evaluate[i]['s_text']

            # On cherche la question correspondante
            associated_question_id = self.dict_answers_to_evaluate[i]['n_question_id']
            # On prend l'enonce de celle-ci
            question_text = self.dict_questions[associated_question_id]['s_text']
            # ainsi que la reponse/solution
            question_clue = self.dict_questions[associated_question_id]['lst_clue_answer'][0]['s_text'] # on prend le premier element parce qu'on ne peut pas encore en ajouter d'autres

            data.append({'text':question_text, 'clue_answer':question_clue, 'answer_to_evaluate':answer_text})

        return data

    @XBlock.json_handler
    def validate_phase1(self, data, suffix=''):
        """
        A handler to validate the phase 1
        """
        print 
        print "Appel au  --> handler 1"
        print "data : ", data

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

        for i in range(9):
            answer_id = self.phase3_answer_indexes[i]
            self.dict_answers_to_evaluate[answer_id]['n_grade'] += int(data[i])
            self.dict_answers_to_evaluate[answer_id]['nb_of_grade'] += 1

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
                'n_grade': 0,
                'nb_of_grade': 0,
            }],
            'n_grade': 0,
            'nb_of_grade': 0,
        }
        # la cle d'un field.Dict passe au format unicode
        self.dict_questions[unicode(self.max_id_question)] = res

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


    def get_prof_questions(self):
        """Return a subset of all questions written by a professor"""
        return dict(filter(lambda k: k[1]['is_prof']==True, self.dict_questions.items()))

    def get_student_questions(self):
        """Return the subset of questions written by students"""
        return dict(filter(lambda k: k[1]['is_prof']==False, self.dict_questions.items()))

    def get_unevaluated_answers(self):
        """Return the subset of questions written by students"""
        return dict(filter(lambda k: k[1]['nb_of_grade']<3, self.dict_answers_to_evaluate.items()))


    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("P3eXBlock",
             """<p3exblock/>
             """),
        ]
