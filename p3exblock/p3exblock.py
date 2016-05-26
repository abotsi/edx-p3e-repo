# coding: utf-8
"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
import os.path
from random import sample, choice, shuffle, randint

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List, Dict
from xblock.fragment import Fragment
import xblock.runtime

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
    dict_students_grade = Dict(
        default={}, scope=Scope.user_state_summary,
        help="The list of grade for each student, "
            +"indexed by student_id.",
    )

# Fields specific to the professor
    studio_data = List(
        default=[], scope=Scope.settings,
        help="The list of (question - answer) submitted by the professor"
            +"that will be copied to dict_questions ASAP."
            +"Not erasable or rewritable, only adding is allowed.",
    )

    display_name = String(
        default="Cooperative Open Pair Assessment", scope=Scope.settings,
        help="Display name"
    )

# Fields specific to one student
    current_phase = Integer(
        default=1, scope=Scope.user_state,
        help="The phase currently running",
    )

    phase1_question_indexes = List(
        default=[], scope=Scope.user_state,
        help="The ids of the 3 questions this student answer in phase 1",
    )
    phase1_answer_indexes = List(
        default=[], scope=Scope.user_state,
        help="The ids of the 3 answers this student submit in phase 1",
    )
    phase2_question_index = Integer(
        default=0, scope=Scope.user_state,
        help="The id of the question this student ask in phase 2",
    )
    phase3_data = List(
        default=[], scope=Scope.user_state,
        help="The 9 triplets (answer id, question id, clue id) referring to what this student correct in phase 3",
    )

    @property 
    def has_score(self):
        """ Needed for this XBlock to be graded """
        return True



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
        """
        The entry point into the LMS (student part of edX).
        """
        print
        print " --> Appel a la student_view"
        print "     Phase n° ", self.current_phase

        # On copie les questions profs vers la liste accessible par les etudiants
        self.update_questions_with_prof_ones()

        # On charge les donnees necessaires a la phase actuelle
        data = []
        if (self.current_phase == 1):
            data = self.get_data_phase1()
        elif (self.current_phase == 3):
            data = self.get_data_phase3()
        elif (self.current_phase == 4):
            self.assess_student_progress(self.runtime.user_id)
            data = self.get_student_grade()

        print "     data : ", data
        print " <-- Fin"
        print

        # On affiche une page d'erreur si il n'y a pas suffisament de donnees pour cette phase
        if (self.current_phase == 1 or self.current_phase == 3) and not data :
            print "     warning : there is not enough data for this phase"
            return self.load_view("error.html")

        return self.load_view("phase"+str(self.current_phase)+".html", data)

    def update_questions_with_prof_ones(self):
        # On recupere le plus grand id de la list des questions prof (le dernier ajoute)
        last_id_created = 0
        if self.studio_data:
            last_id_created = self.studio_data[-1]['id']

        # On ajoute dans dict_q les question de prof qui on un id plus grand que last_id_dict
        if last_id_created > self.last_id_saved:
            print
            print "     Il y a %d nouvelles questions `profs` ! " % last_id_created - self.last_id_saved

            # On parcourt la liste prof depuis la fin
            for new_q_p in reversed(self.studio_data):
                # et on s'arrete quand on trouve un indice qu'on avait deja enregistre
                if new_q_p['id'] <= self.last_id_saved:
                    break
                # On ajoute la nouvelle question dans le dict global
                self.add_studio_question(new_q_p['q'], new_q_p['r'], new_q_p['id'])

            # Puis on met a jour le dernier id qu'on a enregistre
            self.last_id_saved = last_id_created


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
            print
            print "     Phase 1: start picking questions..."
            self.phase1_question_indexes = self.select_questions_phase1()
            print "     Selected questions : ", self.phase1_question_indexes
            print

        lst_txt = []
        for i in self.phase1_question_indexes:
            lst_txt.append(self.get_question_text(i))

        return lst_txt

    def select_questions_phase1(self):
        if len(self.dict_questions)<3:
            print "     there is less than 3 questions"
            return None #peut-etre plutot utiliser un mecanisme style : throw error

        # on prend 3 questions `prof` si il n'y a pas encore de questions `etudiant`
        if len(self.get_student_questions() ) == 0:
            selection = sample(self.get_prof_questions(), 3)
        else:
            selection = sample(self.get_prof_questions(), 2)
            selection.append(sample(self.get_student_questions(), 1)[0]) # [0] --> pour acceder a l'unique element du singleton

        # on melange les questions pour que celle de l'etudiant ne soit pas toujours a la fin
        shuffle(selection)
        return selection


    def get_data_phase3(self, context=None):
        """
        The third phase of the P3E, extracting 9 questions and answers
        """

        # Si on a pas encore tire les reponses
        if not self.phase3_data:
            print
            print "     Phase 3: start picking answers to evaluate..."
            self.phase3_data = self.select_answers_phase3()
            print "     Selected answers : ", self.phase3_data
            print

        data = []
        for e in self.phase3_data:
            answer_text = self.get_answer_text( e['answer_id'] )
            question_text = self.get_question_text( e['question_id'] )
            clue_text = self.get_clue_text( e['question_id'], e['clue_id'] )

            data.append({'text':question_text, 'clue_answer':clue_text, 'answer_to_evaluate':answer_text})

        return data

    def select_answers_phase3(self):        
            # On recupere toutes les reponses non evaluees en enlevant les reponses de l'utilisateur courant
            selection = [elt for elt in self.get_unevaluated_answers() if elt not in self.phase1_answer_indexes ]

            if len(selection) < 9:
                print "     there is less than 9 answers to evaluate"
                return None

            res = []
            for answer_id in sample(selection, 9):
                question_id = self.get_associated_question(answer_id)
                clue_id = self.get_best_clue_index(question_id)
                res.append( {'answer_id':answer_id, 'question_id':question_id, 'clue_id':clue_id} )

            return res

    @XBlock.json_handler
    def validate_phase1(self, data, suffix=''):
        """
        A handler to validate the phase 1
        """
        print
        print " --> Appel au handler 1"
        print "     data : ", data
        print "     self.phase1_question_indexes : ", self.phase1_question_indexes

        for i in range(3):
            question_index = self.phase1_question_indexes[i]

            self.add_grade_to_question(question_index, data[i]['question_grade'])
            print "     grade saved!"

            self.add_answer_to_evaluate(question_index, data[i]['answer'], self.runtime.user_id)
            print "     answer saved!"

            self.phase1_answer_indexes.append(unicode(self.max_id_answer))
            print "     answer id add : ", self.max_id_answer


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

        self.add_question(data['question'], data['answer'], self.runtime.user_id)
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

            self.add_grade_to_answer(answer_id, data['answer_grades'][i])
            graded_student = self.get_answer_writer(answer_id)
            self.assess_student_progress(graded_student)

            self.add_grade_to_clue(question_id, clue_id, data['clue_grades'][i])
            # le cas echeant, on enregistre la nouvelle solution proposee par le correcteur
            if data['new_solutions'][i]:
                self.add_solution(question_id, data['new_solutions'][i])

        self.assess_student_progress(self.runtime.user_id)
        self.current_phase = 4
        print " <-- Fin du handler"

        return self.render_template("phase4.html", self.get_student_grade() )

    def assess_student_progress(self, id_student):
        print " --> Assessing the progress of student n°", id_student

        # recuperer les 3 reponses du meme etudiant
        answers = self.get_answers_of_student(id_student)
        print "     answers of this student : ", answers

        if len(answers)<3:
            print "     This student didn't provide 3 answers."
            return

        student_mean = float(0)
        for a in answers.values():
            print "     a:", a
            # verififer si elles ont ete note 3 fois chacune
            if a['nb_of_grade'] < 3:
                print "     This answer has not been evaluated 3 times."
                return

            # faire la moyenne des evaluations pour chacune reponse
            answer_mean = float(a['n_grade']) / float(a['nb_of_grade'])
            print "     This answer was given the grade of : %s/5" % answer_mean
            student_mean += answer_mean

        # raporter la note des 3 reponses en une note sur 20
        student_mean = student_mean / float(3*5) * 20
        print "     This student was given the grade of : %s/20" % student_mean

        # self.runtime.publish(self, "grade", 
        #                     { 
        #                         'value': student_mean,
        #                         'max_value': 20, 
        #                         'user_id': id_student,
        #                     })
        # print "     Grade publish !"
        self.dict_students_grade[id_student] = student_mean


    def add_question(self, p_question_txt, p_answer_txt, p_writer_id, p_is_prof=False):
        if p_writer_id is None:
            p_writer_id = -1

        self.max_id_question+=1
        res = {
            'n_writer_id': unicode(p_writer_id),
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

    def add_answer_to_evaluate(self, id_question, p_s_text, p_writer_id):
        if p_writer_id is None:
            p_writer_id = -1

        self.max_id_answer+=1
        res = {
            'n_question_id': unicode(id_question),
            'n_writer_id': unicode(p_writer_id),
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

    def add_grade_to_question(self, id_question, value):
        self.dict_questions[id_question]['n_grade'] += int(value)
        self.dict_questions[id_question]['nb_of_grade'] += 1

    def add_grade_to_answer(self, id_answer, value):
        self.dict_answers_to_evaluate[id_answer]['n_grade'] += int(value)
        self.dict_answers_to_evaluate[id_answer]['nb_of_grade'] += 1
    
    def add_grade_to_clue(self, id_question, id_clue, value):
        self.dict_questions[id_question]['lst_clue_answer'][id_clue]['n_grade'] += int(value)
        self.dict_questions[id_question]['lst_clue_answer'][id_clue]['nb_of_grade'] += 1


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

    def get_nb_of_grade(self, id_answer):
        return self.dict_answers_to_evaluate[id_answer]['nb_of_grade']

    def get_associated_question(self, id_answer):
        return self.dict_answers_to_evaluate[id_answer]['n_question_id']

    def get_answer_writer(self, id_answer):
        return self.dict_answers_to_evaluate[id_answer]['n_writer_id']

    def get_answers_of_student(self, student_id):
        return dict(filter(lambda k: k[1]['n_writer_id']==unicode(student_id), self.dict_answers_to_evaluate.items()))


    def get_question_text(self, id_question):
        return self.dict_questions[id_question]['s_text']

    def get_answer_text(self, id_answer):
        return self.dict_answers_to_evaluate[id_answer]['s_text']

    def get_clue_text(self, id_question, id_clue):
        return self.dict_questions[id_question]['lst_clue_answer'][id_clue]['s_text']

    def get_student_grade(self):
        if self.runtime.user_id in self.dict_students_grade:
            return self.dict_students_grade[self.runtime.user_id]
        else:
            return None


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
